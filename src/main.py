import argparse

from colorama import init

from app import bootstrap
from constants import PATH_PROFILES, PATH_DEBUG
from menu import menu
from utils import load_config


if __name__ == '__main__':
    init()

    for path in (PATH_PROFILES, PATH_DEBUG):
        path.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description='Help of ow-league-tokens')
    parser.add_argument(
        '--nomenu',
        help='Run app without menu using config',
        action='store_true',
    )

    args = parser.parse_args()

    if args.nomenu:
        config = load_config()
        bootstrap(config)
    else:
        menu()
