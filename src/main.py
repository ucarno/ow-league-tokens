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
from constants import OWL_TRACK_URL, OWC_TRACK_URL, OWC_CHECK_URL, OWL_CHECK_URL, USERS_API_URL
from farmer import Farmer
from utils import print_fmt


def start_bot(earn_owl: bool, earn_owc: bool, account_ids: list[int], debug: bool):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='[%(asctime)s - %(levelname)s] %(message)s'
    )

    print_fmt(f'\n  !!! Starting bot for &n{len(account_ids)}&r account(s) !!!')
    print_fmt('    League Tokens earning is ' + (f'&sEnabled' if earn_owl else f'&fDisabled') + '&r')
    print_fmt('    Contenders Skins earning is ' + ('&sEnabled' if earn_owc else '&fDisabled') + '&r')

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
        print_fmt('Bye!')
        exit()


def menu(args):
    c = Config()

    start_text = '&sStart&r'
    stop_text = '&fStop&r'

    earning = '&n[earning]&r'
    not_earning = '&n[not earning]&r'

    def interrupt(t: str):
        print_fmt(t)
        sleep(0.5)  # adding a little delay so user can see that something happened
        print()

    while True:
        print_fmt('&nSelect an option:&r')

        bot_text = 'Start bot!'
        if not c.config['accounts']:
            bot_text += ' &f(no accounts added!)&r'
        else:
            bot_text += f' &n[{len(c.config["accounts"])} account(s)]&r'
        if not any([c.config['earn_owl'], c.config['earn_owc']]):
            bot_text += ' &f(nothing to earn!)&r'

        menu_entries = [
            # option 0
            bot_text,

            # option 1
            '&s(+)&r Add an account by username &f(NOT WORKING)',

            # option 2
            '&s(+)&r Add an account manually (using account ID)',

            # option 3
            '&f(-)&r Remove an account' + (
                f' &f(no accounts added!)&r' if not c.config['accounts'] else ''
            ),

            # option 4
            'List your accounts',

            # option 5
            f'{stop_text if c.config["earn_owl"] else start_text} earning OWL Tokens '
            f'{earning if c.config["earn_owl"] else not_earning}',

            # option 6
            f'{stop_text if c.config["earn_owc"] else start_text} earning Contenders Skins '
            f'{earning if c.config["earn_owc"] else not_earning} &e(experimental!*)&r',

            # option 7
            f'{"&fDisable" if c.config["debug"] else "&sEnable"}&r debug messages '
            f'&n[{"enabled" if c.config["debug"] else "disabled"}]&r',

            # option 8
            'Exit',
        ]
        menu_str = '\n'.join([f'  &o{i+1}.&r {e}' for i, e in enumerate(menu_entries)])

        print_fmt(menu_str)

        try:
            option = int(input(' >>> ')) - 1
            if option not in range(len(menu_entries)):
                raise ValueError
        except ValueError:
            interrupt('&fInvalid number.&r')
            continue

        # starting bot
        if option == 0:
            if not c.config['accounts']:
                interrupt('&fTo start a bot, add at least one account first.&r')
                continue

            if not any([c.config['earn_owl'], c.config['earn_owc']]):
                interrupt('&fYou need to enable option 4 and/or 5 in order to start a bot.&r')
                continue

            start_bot(
                earn_owl=c.config['earn_owl'],
                earn_owc=c.config['earn_owc'],
                account_ids=[int(i) for i in c.config['accounts'].keys()],
                debug=c.config['debug']
            )

        # adding an account
        elif option == 1:
            print_fmt('\n&nAdding an account...&r')
            interrupt('&fBlizzard has made changes to their profiles API, so ID is now irretrievable this way. '
                      'Consider manually getting your ID and using &eoption 3&f. '
                      'To get your ID, just follow instructions from here: '
                      '&ehttps://github.com/ucarno/ow-league-tokens#manually-getting-your-account-id')
            continue

            # leaving the code in case there is another way of retrieving ID using username or API will change
            while True:
                print_fmt('What is your username? (for example &nmyUsername&r or &nmyUsername#1234&r) '
                      '- leave &oblank&r to exit')

                leave_text = '&sAlright!&r'

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
                        interrupt('&fIt seems that profiles API that is used to retrieve your account ID '
                                  'is currently under maintenance. Consider adding your account manually.&r')
                        user_dict = None
                        break

                if not users:
                    print_fmt('&fUsers with that username not found.&r', end='\n\n')
                    continue

                if len(users) == 1:
                    user_dict = users[0]
                else:
                    print_fmt(f'Found &n{len(users)}&r users with that username. You are..?')
                    for index, item in enumerate(users):
                        print_fmt(f'  &o{index + 1}.&r &n{item["battleTag"]}&r')
                    print_fmt('&o  Leave blank to leave&r')

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
                            print_fmt('&fInvalid number.&r')
                            continue
                        user_dict = users[int(number) - 1]
                        break

                if user_dict is None:
                    break

                account_id = str(user_dict['id'])
                if account_id in c.config['accounts']:
                    interrupt('&fThis account is already added!&r')
                    break

                else:
                    c.config['accounts'][account_id] = {
                        'username': user_dict['name'],
                        'level': user_dict['playerLevel'],
                        'platform': user_dict['platform'],
                    }
                    c.save()
                    print_fmt('&sAccount added!&r')

                    print_fmt('\nWant to add more? &n(y/N)&r')
                    add_more = input(' >>> ').lower() == 'y'

                    print()

                    if add_more:
                        continue
                    break

        # adding an account manually (using ID)
        elif option == 2:
            print_fmt('\n&nAdding an account using account ID&r')
            print_fmt('Where to get your account ID: '
                      'https://github.com/ucarno/ow-league-tokens#manually-getting-your-account-id')

            leave_text = '&sAlright!&r'

            print_fmt('&oEnter your account ID (leave blank to exit):&r')

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
                    print_fmt('&fAccount ID must be a number.&r')
                    continue

                else:
                    c.config['accounts'][number] = {'username': f'ID:{number}'}
                    c.save()
                    print_fmt('&sAccount added!&r')

                    print_fmt('\nWant to add more? &n(y/N)&r')
                    add_more = input(' >>> ').lower() == 'y'

                    print()

                    if add_more:
                        print_fmt('&oEnter your account ID (leave blank to exit):&r')
                        continue
                    break

        # removing an account
        elif option == 3:
            print_fmt('\n&nAccount removal:&r')

            accounts = c.config['accounts']
            if len(accounts) == 0:
                interrupt('&fThere are no accounts to remove.&r')

            # 1 account, deleting
            elif len(accounts) == 1:
                accounts.clear()
                c.save()
                interrupt('&sAccount removed!&r')

            # more than 1 account
            else:
                print_fmt('What account do you want to remove?')
                accounts = [(key, value) for key, value in accounts.items()]
                accounts_str = '\n'.join([f'  &o{i + 1}.&r {a[1]["username"]} ' for i, a in enumerate(accounts)])

                print_fmt(accounts_str)
                print_fmt('&oLeave blank to exit.&r')
                print_fmt('&oType \'&n*&o\' to remove all accounts.&r')

                leave_text = '&sAlright!&r'

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
                        interrupt('&sAll accounts removed!&r')
                        break

                    if not number.isdigit() or int(number)-1 not in range(len(accounts)):
                        print_fmt('&fInvalid number.&r')
                        continue

                    account_id = accounts[int(number)-1][0]
                    del c.config['accounts'][account_id]
                    c.save()
                    interrupt('&sAccount removed!&r')
                    break

        elif option == 4:
            print_fmt('\n&nList of your accounts:&r')

            accounts = c.config['accounts']
            if len(accounts) == 0:
                interrupt('&fThere are no accounts.&r')

            accounts = [(key, value) for key, value in accounts.items()]
            accounts_str = '\n'.join([f'  &o{i + 1}.&r {a[1]["username"]} ' for i, a in enumerate(accounts)])
            interrupt(accounts_str)

        # switching owl tokens
        elif option == 5:
            print_fmt('\n&nLeague Tokens:&r')
            text = f'You will &fno longer earn&r League Tokens.' if c.config['earn_owl'] else \
                   'You will &snow earn&r League Tokens!'
            c.config['earn_owl'] = not c.config['earn_owl']
            c.save()
            interrupt(text)

        # switching owc skins
        elif option == 6:
            print_fmt('\n&nContenders Skins:&r')
            text = f'You will &fno longer earn&r Contenders Skins.' if c.config['earn_owc'] else \
                   'You will &snow earn&r Contenders Skins!'
            c.config['earn_owc'] = not c.config['earn_owc']

            if c.config['earn_owc']:
                print_fmt('&fPlease note that contenders skins earning is not working for now (18.12.2022). '
                          'It may and may not occasionally start working in future, no one knows. '
                          'You can find more info about this issue here: '
                          '&ehttps://github.com/shirokumacode/overwatch-omnic-rewards/issues/28#issuecomment-1194812086&r')

            c.save()
            interrupt(text)

        elif option == 7:
            print_fmt('\n&nDebug messages:&r')
            text = f'You will {("&fno longer see" if c.config["debug"] else "&snow see")}&r debug messages.'
            c.config['debug'] = not c.config['debug']
            c.save()
            interrupt(text)

        elif option == 8:
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
        print_fmt('&fMissing account ids. '
              'Account IDs must be specified either in config or via \'--ids\' command line argument.&r')
        exit()

    earn_owl = c.config['earn_owl'] if args.owl is None else args.owl
    earn_owc = c.config['earn_owc'] if args.owc is None else args.owc

    if not any([earn_owl, earn_owc]):
        print_fmt('&fYou need to specify what to earn (tokens, skins or both).&r')
        exit()

    start_bot(
        earn_owl=earn_owl,
        earn_owc=earn_owc,
        account_ids=account_ids,
        debug=c.config['debug'] if args.debug is None else args.debug
    )


if __name__ == '__main__':
    init()

    parser = argparse.ArgumentParser(description='Overwatch League Tokens Farmer help')
    parser.set_defaults(func=menu)

    subparsers = parser.add_subparsers()
    nomenu_parser = subparsers.add_parser('nomenu', help='Run program without opening menu')
    nomenu_parser.set_defaults(func=no_menu)

    nomenu_parser.add_argument(
        '--owl',
        help='earn league tokens, default value is \'true\'',
        default=None,
        action=argparse.BooleanOptionalAction
    )
    nomenu_parser.add_argument(
        '--owc',
        help='earn contenders skins, default value is \'true\'',
        default=None,
        action=argparse.BooleanOptionalAction
    )
    nomenu_parser.add_argument(
        '--debug',
        help='show debug messages, default value is \'false\'',
        default=None,
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
        print_fmt('\nBye!')
        exit()
