import argparse
import os
import sys

from colorama import init

from app import bootstrap
from constants import PATH_PROFILES, PATH_DEBUG, PATH_ROOT, DISCORD_URL, DOCKER_CHROMIUM_FLAGS
from macos import setup_macos_certs
from menu import menu
from utils import load_config, get_console_message

if __name__ == '__main__':
    # fix requests module not able to find certs in lib folder
    if hasattr(sys, 'frozen'):
        os.environ['REQUESTS_CA_BUNDLE'] = (
            str(PATH_ROOT.joinpath('lib').joinpath('certifi').joinpath('cacert.pem').absolute())
        )

        if sys.platform.startswith('darwin'):
            check_path = PATH_ROOT.joinpath('macos_certs.txt')
            if not check_path.exists():
                setup_macos_certs()
                with open(check_path, 'w+', encoding='utf-8') as f:
                    f.write('This files indicates that CA Certificates are set up.')
                    f.close()

    init()
    print(get_console_message(
        f'&mJoin our Discord for help, updates, suggestions, instructions and more: &g{DISCORD_URL}'
    ))

    for path in (PATH_PROFILES, PATH_DEBUG):
        path.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description='Help of ow-league-tokens')
    parser.add_argument(
        '--nomenu',
        help='Run app without menu using config',
        action='store_true',
    )
    parser.add_argument(
        '--nowait',
        help='App will not wait for Enter key press on error',
        action='store_true',
    )
    parser.add_argument(
        '--docker',
        help='Specifying this argument will include additional Chromium flags that will make Docker work '
             '(works only with `--nomenu` argument)',
        action='store_true',
    )
    parser.add_argument(
        '--profiles',
        help='Specify profiles to use instead of taking them from `config.json` (works only with `--nomenu` argument)',
        nargs='+',
        type=str,
        default=[],
    )

    args = parser.parse_args()

    if args.nomenu:
        config = load_config()
        if args.profiles:
            config['profiles'] = args.profiles
        if args.docker:
            config['chromium_flags'].extend(DOCKER_CHROMIUM_FLAGS)
            config['headless'] = False
        bootstrap(config, args.nowait)
    else:
        menu()
