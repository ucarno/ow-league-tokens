import os

from app import bootstrap
from constants import PATH_PROFILES
from utils import get_console_message, load_config, save_config


P = lambda msg: print(get_console_message('&y' + msg))
cls = lambda: os.system('cls' if os.name == 'nt' else 'clear')
wait_for_enter = lambda: input('\nPress Enter...\n')
get_input = lambda: input(' >> ')


def add_profile(config):
    cls()

    allowed_characters = set(list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'))
    allowed_chars_repr = '&gA-Z&r, &ga-z&r, &g0-9&r, &g-&r, &g_&r'
    P('One account - one (Gmail) profile. '
      'I recommend adding one account at a time so you know what account you log into.')
    while True:
        P(f'Enter profile name (allowed characters: {allowed_chars_repr.replace("&r", "&y")}) or leave blank to exit:')
        name = get_input()

        if not name:
            return

        if len(set(list(name)) - allowed_characters) > 0:
            P(f'&rProfile name contains forbidden characters! Allowed characters are {allowed_chars_repr}&r.\n')
            continue

        if name in config['profiles']:
            P(f'&rProfile \'{name}\' already exists!\n')
            continue

        config['profiles'].append(name)
        save_config(config)
        P('&gProfile added!\n')
        continue


def view_profiles(config):
    cls()

    if len(config['profiles']) == 0:
        P('&rNo profiles!')
        wait_for_enter()

    P('Your profiles:')
    for profile in config['profiles']:
        P(f'    &c{profile}')

    wait_for_enter()


def remove_profile(config):
    if len(config['profiles']) == 0:
        P('&rNo profiles!')
        wait_for_enter()
        return

    cls()

    P('You are gonna remove your profile. Profile will not be deleted (just disabled), you can re-add it later. '
      f'To remove profile completely, delete profile from &g{PATH_PROFILES.absolute()}&y directory.')

    while True:
        if len(config['profiles']) == 0:
            return

        P('\nYour profiles:')
        for index, profile in enumerate(config['profiles']):
            P(f'    {index + 1}. &c{profile}')

        P('\nChoose profile to remove (leave blank to exit):')
        profile_idx = get_input()
        if not profile_idx:
            return

        profile_count = len(config['profiles'])
        if not profile_idx.isdigit() or not 0 < int(profile_idx) <= profile_count:
            P('\n&rInvalid profile number!')
            continue

        profile_idx = int(profile_idx) - 1
        config['profiles'].pop(profile_idx)
        save_config(config)
        P('\n&gProfile removed!')

        if len(config['profiles']) == 0:
            return


def switch_setting(config, setting):
    config[setting] = not config[setting]
    save_config(config)


def menu():
    config = load_config()

    while True:
        options = [
            (
                f'Start app!',
                lambda c: bootstrap(c)
            ),
            (
                f'Add profile &g[+]',
                add_profile
            ),
            (
                f'Remove profile &r[{"-" if len(config["profiles"]) else "-"}]',
                remove_profile,
            ),
            (
                f'View profiles {"&g" if len(config["profiles"]) else "&r"}[{len(config["profiles"])} profile(s)]',
                view_profiles
            ),
            (
                f'Switch headless mode {"&g[enabled]" if config["headless"] else "&r[disabled]"} &m(experimental!)',
                lambda c: switch_setting(c, 'headless')
            ),
            (
                f'Switch debug mode {"&g[enabled]" if config["debug"] else "&r[disabled]"}',
                lambda c: switch_setting(c, 'debug')
            ),
            (
                f'Exit',
                lambda c: exit()
            )
        ]

        cls()
        P('&cSelect an option:')
        for index, (option_name, _) in enumerate(options):
            P(f'    &c{index + 1}. &y{option_name}')

        option = input(' >> ')

        if not option or not option.isdigit() or not 0 < int(option) <= len(options):
            P('&rInvalid option!')
            wait_for_enter()

        option_idx = int(option) - 1
        option_callback = options[option_idx][1]
        option_callback(config)  # noqa

        continue
