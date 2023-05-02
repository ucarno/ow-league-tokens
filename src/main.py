import argparse
import os
import sys

from colorama import init

from app import bootstrap
from constants import PATH_PROFILES, PATH_DEBUG, PATH_ROOT
from menu import menu
from utils import load_config


if __name__ == '__main__':
    # fix requests module not able to find certs in lib folder
    if hasattr(sys, 'frozen'):
        os.environ['REQUESTS_CA_BUNDLE'] = (
            str(PATH_ROOT.joinpath('lib').joinpath('certifi').joinpath('cacert.pem').absolute())
        )

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
