from pathlib import Path

from colorama import Fore

CURRENT_VERSION = '0.1'

DEBUG_ENVIRON = 'OW_LEAGUE_TOKENS_DEBUG'

PATH_ROOT = Path(__file__).parent
PATH_PROFILES = PATH_ROOT.joinpath('profiles')
PATH_DEBUG = PATH_ROOT.joinpath('debug')
PATH_CONFIG = PATH_ROOT.joinpath('config.json')

TEST_CHANNEL_ID = 'UCaG0IHN1RMOZ4-U3wDXAkwA'
OWL_CHANNEL_ID = 'UCiAInBL9kUzz1XRxk66v-gw'
# OWL_CHANNEL_ID = TEST_CHANNEL_ID
OWC_CHANNEL_ID = 'UCWPW0pjx6gncOEnTW8kYzrg'

TMPL_LIVE_STREAM_EMBED_URL = 'https://www.youtube.com/embed/live_stream?channel=%s'
TMPL_LIVE_STREAM_URL = 'https://www.youtube.com/watch?v=%s'

VERSION_CHECK_URL = 'https://raw.githubusercontent.com/ucarno/ow-league-tokens/main/version.txt'
VERSION_ENVIRON = 'OW_LEAGUE_TOKENS_NEW_VERSION'

YOUTUBE_LOGIN_URL = 'https://accounts.google.com/ServiceLogin?service=youtube&continue=https%3A%2F%2Fwww.youtube.com'

YOUTUBE_AUTH_PASS = 'https://www.youtube.com'
YOUTUBE_AUTH_FAIL = 'https://accounts.google.com'

YOUTUBE_AUTH_PASS_RE = YOUTUBE_AUTH_PASS.replace('/', r'\/')
YOUTUBE_AUTH_FAIL_RE = YOUTUBE_AUTH_FAIL.replace('/', r'\/')
YOUTUBE_AUTH_ANY_RE = f'^({YOUTUBE_AUTH_PASS_RE}|{YOUTUBE_AUTH_FAIL_RE})'
YOUTUBE_AUTH_PASS_RE = '^' + YOUTUBE_AUTH_PASS_RE


COLORS = (
    ('&g', Fore.GREEN),
    ('&r', Fore.RED),
    ('&c', Fore.CYAN),
    ('&y', Fore.YELLOW),
    ('&m', Fore.MAGENTA),
    ('&!r', Fore.RESET),
)
