import argparse
import asyncio
import json
import logging
import os
import urllib.request
import urllib.parse
from json import JSONDecodeError
from time import sleep
from sys import exit

from colorama import init

from config import Config
from constants import (
    COLOR_NEUTRAL, COLOR_RESET, COLOR_FAILURE, COLOR_SUCCESS, COLOR_OPTIONS, COLOR_EXPERIMENTAL,
    OWL_TRACK_URL, OWC_TRACK_URL, OWC_CHECK_URL, OWL_CHECK_URL, USERS_API_URL
)
from farmer import Farmer


def start_bot(earn_owl: bool, earn_owc: bool, account_ids: list[int]):
    print(f'\n  !!! Starting bot for {COLOR_NEUTRAL}{len(account_ids)}{COLOR_RESET} account(s) !!!')
    print('    League Tokens earning is ' +
         (f'{COLOR_SUCCESS}Enabled' if earn_owl else f'{COLOR_FAILURE}Disabled') + COLOR_RESET)
    print('    Contenders Skins earning is ' +
         (f'{COLOR_SUCCESS}Enabled' if earn_owc else f'{COLOR_FAILURE}Disabled') + COLOR_RESET)

    sleep(1)
    print()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if earn_owl:
        farmer_owl = Farmer(
            prefix='OWL',
            check_url=OWL_CHECK_URL,
            track_url=OWL_TRACK_URL,
            account_ids=account_ids,
            check_sentinel=False,
            check_if_live=False,  # always track, ignore fake "not live" data
        )
        loop.create_task(farmer_owl.run())

    if earn_owc:
        farmer_owc = Farmer(
            prefix='OWC',
            check_url=OWC_CHECK_URL,
            track_url=OWC_TRACK_URL,
            account_ids=account_ids,
            check_sentinel=False,
            check_if_live=True,  # stream is always "available", so checking if live
        )
        loop.create_task(farmer_owc.run())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Bye!')
        exit()


def menu(args):
    c = Config()

    start_text = f'{COLOR_SUCCESS}Start{COLOR_RESET}'
    stop_text = f'{COLOR_FAILURE}Stop{COLOR_RESET}'

    earning = f'{COLOR_NEUTRAL}[earning]{COLOR_RESET}'
    not_earning = f'{COLOR_NEUTRAL}[not earning]{COLOR_RESET}'

    def interrupt(t: str):
        print(t, end='\n')
        sleep(0.5)  # adding a little delay so user can see that something happened
        print()

    while True:
        print(f'{COLOR_NEUTRAL}Select an option:{COLOR_RESET}')

        bot_text = 'Start bot!'
        if not c.config['accounts']:
            bot_text += f' {COLOR_FAILURE}(no accounts added!){COLOR_RESET}'
        else:
            bot_text += f' {COLOR_NEUTRAL}[{len(c.config["accounts"])} account(s)]{COLOR_RESET}'
        if not any([c.config['earn_owl'], c.config['earn_owc']]):
            bot_text += f' {COLOR_FAILURE}(nothing to earn!){COLOR_RESET}'

        menu_entries = [
            # option 0
            bot_text,

            # option 1
            f'{COLOR_SUCCESS}(+){COLOR_RESET} Add an account',

            # option 2
            f'{COLOR_SUCCESS}(+){COLOR_RESET} Add an account manually (using account ID)',

            # option 3
            f'{COLOR_FAILURE}(-){COLOR_RESET} Remove an account' + (
                f' {COLOR_FAILURE}(no accounts added!){COLOR_RESET}' if not c.config['accounts'] else ''
            ),

            # option 4
            f'List your accounts',

            # option 5
            f'{stop_text if c.config["earn_owl"] else start_text} earning OWL Tokens '
            f'{earning if c.config["earn_owl"] else not_earning}',

            # option 6
            f'{stop_text if c.config["earn_owc"] else start_text} earning Contenders Skins '
            f'{earning if c.config["earn_owc"] else not_earning} '
            f'{COLOR_EXPERIMENTAL}(experimental!){COLOR_RESET}',

            # option 7
            'Exit',
        ]
        menu_str = '\n'.join([f'  {COLOR_OPTIONS}{i+1}.{COLOR_RESET} {e}' for i, e in enumerate(menu_entries)])

        print(menu_str)

        try:
            option = int(input(' >>> ')) - 1
            if option not in range(len(menu_entries)):
                raise ValueError
        except ValueError:
            interrupt(f'{COLOR_FAILURE}Invalid number.{COLOR_RESET}')
            continue

        # starting bot
        if option == 0:
            if not c.config['accounts']:
                interrupt(f'{COLOR_FAILURE}To start a bot, add at least one account first.{COLOR_RESET}')
                continue

            if not any([c.config['earn_owl'], c.config['earn_owc']]):
                interrupt(f'{COLOR_FAILURE}You need to enable option 4 and/or 5 '
                          f'in order to start a bot.{COLOR_RESET}')
                continue

            start_bot(
                earn_owl=c.config['earn_owl'],
                earn_owc=c.config['earn_owc'],
                account_ids=[int(i) for i in c.config['accounts'].keys()],
            )

        # adding an account
        elif option == 1:
            print(f'\n{COLOR_NEUTRAL}Adding an account...{COLOR_RESET}')
            while True:
                print(f'What is your username? (for example {COLOR_NEUTRAL}myUsername{COLOR_RESET} '
                      f'or {COLOR_NEUTRAL}myUsername#1234{COLOR_RESET}) '
                      f'- leave {COLOR_OPTIONS}blank{COLOR_RESET} to exit')

                leave_text = f'{COLOR_SUCCESS}Alright!{COLOR_RESET}'

                try:
                    username = input(' >>> ').strip()
                except KeyboardInterrupt:
                    interrupt(leave_text)
                    break

                if not username:
                    interrupt(leave_text)
                    break

                url = USERS_API_URL % (urllib.parse.quote(username),)

                with urllib.request.urlopen(url) as response:
                    response_text = response.read()
                    try:
                        users: list = json.loads(response_text)
                    except JSONDecodeError:
                        interrupt(f'{COLOR_FAILURE}It seems that profiles API that is used to retrieve your account ID '
                                  f'is currently under maintenance. Consider adding your account manually.{COLOR_RESET}')
                        user_dict = None
                        break

                if not users:
                    print(f'{COLOR_FAILURE}Users with that username not found.{COLOR_RESET}', end='\n\n')
                    continue

                if len(users) == 1:
                    user_dict = users[0]
                else:
                    print(f'Found {COLOR_NEUTRAL}{len(users)}{COLOR_RESET} users with that username. You are..?')
                    for index, item in enumerate(users):
                        print(f'  {COLOR_OPTIONS}{index + 1}.{COLOR_RESET} {COLOR_NEUTRAL}{item["name"]}{COLOR_RESET} '
                              f'(level: {item["playerLevel"]}, '
                              f'platform: {item["platform"].upper()})')
                    print(f'{COLOR_OPTIONS}  Leave blank to leave{COLOR_RESET}')

                    while True:
                        try:
                            number = input(' >>> ')
                        except KeyboardInterrupt:
                            interrupt(leave_text)
                            user_dict = None
                            break

                        if not number:
                            interrupt(leave_text)
                            user_dict = None
                            break

                        if not number.isdigit() or int(number) - 1 not in range(len(users)):
                            print(f'{COLOR_FAILURE}Invalid number.{COLOR_RESET}')
                            continue
                        user_dict = users[int(number) - 1]
                        break

                if user_dict is None:
                    break

                account_id = str(user_dict['id'])
                if account_id in c.config['accounts']:
                    interrupt(f'{COLOR_FAILURE}This account is already added!{COLOR_RESET}')
                    break

                else:
                    c.config['accounts'][account_id] = {
                        'username': user_dict['name'],
                        'level': user_dict['playerLevel'],
                        'platform': user_dict['platform'],
                    }
                    c.save()
                    print(f'{COLOR_SUCCESS}Account added!{COLOR_RESET}')

                    print(f'\nWant to add more? {COLOR_NEUTRAL}(y/N){COLOR_RESET}')
                    add_more = input(' >>> ').lower() == 'y'

                    print()

                    if add_more:
                        continue
                    break

        # adding an account manually (using ID)
        elif option == 2:
            print(f'\n{COLOR_NEUTRAL}Adding an account using account ID{COLOR_RESET}')
            print('Where to get your account ID: '
                  'https://github.com/ucarno/ow-league-tokens#manually-getting-your-account-id')

            leave_text = f'{COLOR_SUCCESS}Alright!{COLOR_RESET}'

            print(f'{COLOR_OPTIONS}Enter your account ID (leave blank to exit):{COLOR_RESET}')

            while True:
                try:
                    number = input(' >>> ')
                except KeyboardInterrupt:
                    interrupt(leave_text)
                    break

                if number.strip() == '':
                    interrupt(leave_text)
                    break

                number = number.strip()
                if not number.isdigit() or int(number) < 1:
                    print(f'{COLOR_FAILURE}Account ID must be a number.{COLOR_RESET}')
                    continue

                else:
                    c.config['accounts'][number] = {
                        'username': f'ID:{number}',
                        'level': '???',
                        'platform': '???',
                    }
                    c.save()
                    print(f'{COLOR_SUCCESS}Account added!{COLOR_RESET}')

                    print(f'\nWant to add more? {COLOR_NEUTRAL}(y/N){COLOR_RESET}')
                    add_more = input(' >>> ').lower() == 'y'

                    print()

                    if add_more:
                        print(f'{COLOR_OPTIONS}Enter your account ID (leave blank to exit):{COLOR_RESET}')
                        continue
                    break

        # removing an account
        elif option == 3:
            print(f'\n{COLOR_NEUTRAL}Account removal{COLOR_RESET}')

            accounts = c.config['accounts']
            if len(accounts) == 0:
                interrupt(f'{COLOR_FAILURE}There are no accounts to remove.{COLOR_RESET}')

            # 1 account, deleting
            elif len(accounts) == 1:
                accounts.clear()
                c.save()
                interrupt(f'{COLOR_SUCCESS}Account removed!{COLOR_RESET}')

            # more than 1 account
            else:
                print('What account do you want to remove?')
                accounts = [(key, value) for key, value in accounts.items()]
                accounts_str = '\n'.join([(
                    f'  {COLOR_OPTIONS}{i + 1}.{COLOR_RESET} {a[1]["username"]} '
                    f'({a[1]["platform"].upper()} - LVL {a[1]["level"]}+)'
                ) for i, a in enumerate(accounts)])

                print(accounts_str)
                print(f'{COLOR_OPTIONS}Leave blank to exit.{COLOR_RESET}')
                print(f'{COLOR_OPTIONS}Type \'{COLOR_NEUTRAL}*{COLOR_OPTIONS}\' to remove all accounts.{COLOR_RESET}')

                leave_text = f'{COLOR_SUCCESS}Alright!{COLOR_RESET}'

                while True:
                    try:
                        number = input(' >>> ')
                    except KeyboardInterrupt:
                        interrupt(leave_text)
                        break

                    if number.strip() == '':
                        interrupt(leave_text)
                        break

                    if number == '*':
                        c.config['accounts'].clear()
                        c.save()
                        interrupt(f'{COLOR_SUCCESS}All accounts removed!{COLOR_RESET}')
                        break

                    if not number.isdigit() or int(number)-1 not in range(len(accounts)):
                        print(f'{COLOR_FAILURE}Invalid number.{COLOR_RESET}')
                        continue

                    account_id = accounts[int(number)-1][0]
                    del c.config['accounts'][account_id]
                    c.save()
                    interrupt(f'{COLOR_SUCCESS}Account removed!{COLOR_RESET}')
                    break

        elif option == 4:
            print(f'\n{COLOR_NEUTRAL}List of your accounts{COLOR_RESET}')

            accounts = c.config['accounts']
            if len(accounts) == 0:
                interrupt(f'{COLOR_FAILURE}There are no accounts.{COLOR_RESET}')

            accounts = [(key, value) for key, value in accounts.items()]
            accounts_str = '\n'.join([(
                f'  {COLOR_OPTIONS}{i + 1}.{COLOR_RESET} {a[1]["username"]} '
                f'({a[1]["platform"].upper()} - LVL {a[1]["level"]}+)'
            ) for i, a in enumerate(accounts)])
            interrupt(accounts_str)

        # switching owl tokens
        elif option == 5:
            print(f'\n{COLOR_NEUTRAL}League Tokens{COLOR_RESET}')
            text = f'You will {COLOR_FAILURE}no longer earn{COLOR_RESET} League Tokens.' if c.config['earn_owl'] else \
                   f'You will {COLOR_SUCCESS}now earn{COLOR_RESET} League Tokens!'
            c.config['earn_owl'] = not c.config['earn_owl']
            c.save()
            interrupt(text)

        # switching owc skins
        elif option == 6:
            print(f'\n{COLOR_NEUTRAL}Contenders Skins{COLOR_RESET}')
            text = f'You will {COLOR_FAILURE}no longer earn{COLOR_RESET} Contenders Skins.' if c.config['earn_owc'] else \
                   f'You will {COLOR_SUCCESS}now earn{COLOR_RESET} Contenders Skins!'
            c.config['earn_owc'] = not c.config['earn_owc']
            c.save()
            interrupt(text)

        elif option == 7:
            print('Bye!')
            exit()


def no_menu(args):
    c = Config()

    if args.ids:
        account_ids = args.ids
    elif 'ids' in os.environ: 
        account_ids = os.environ.get('ids').split()
    else:
        account_ids = [int(i) for i in c.config['accounts'].keys()]

    if not account_ids:
        print(f'{COLOR_FAILURE}Missing account ids. '
              f'Account IDs must be specified either in config or via \'--ids\' command line argument.{COLOR_RESET}')
        exit()

    earn_owl = c.config['earn_owl'] if args.owl is None else args.owl
    earn_owc = c.config['earn_owc'] if args.owc is None else args.owc

    if not any([earn_owl, earn_owc]):
        print(f'{COLOR_FAILURE}You need to specify what to earn (tokens, skins or both).{COLOR_RESET}')
        exit()

    start_bot(
        earn_owl=earn_owl,
        earn_owc=earn_owc,
        account_ids=account_ids,
    )


if __name__ == '__main__':
    init()

    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s - %(levelname)s] %(message)s'
    )

    parser = argparse.ArgumentParser(description='Overwatch League Tokens Farmer help')
    parser.set_defaults(func=menu)

    subparsers = parser.add_subparsers()
    nomenu_parser = subparsers.add_parser('nomenu', help='Run program without opening menu')
    nomenu_parser.set_defaults(func=no_menu)

    nomenu_parser.add_argument(
        '--owl',
        help='earn league tokens, default value is \'true\'',
        default=True,
        action=argparse.BooleanOptionalAction
    )
    nomenu_parser.add_argument(
        '--owc',
        help='earn contenders skins, default value is \'true\'',
        default=True,
        action=argparse.BooleanOptionalAction
    )
    nomenu_parser.add_argument(
        '--ids',
        type=int,
        help='use specified account IDs instead of IDs from config',
        nargs='+'
    )

    parsed_args = parser.parse_args()

    try:
        parsed_args.func(parsed_args)
    except KeyboardInterrupt:
        print('\nBye!')
        exit()
