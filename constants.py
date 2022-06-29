from colorama import Fore

OWL_CHECK_URL = 'https://overwatchleague.com/en-us/'
OWC_CHECK_URL = 'https://overwatchleague.com/en-us/contenders'

# url from some js chunk
OWL_TRACK_URL = 'https://pk0yccosw3.execute-api.us-east-2.amazonaws.com/production/v2/sentinel-tracking/owl'
OWC_TRACK_URL = 'https://pk0yccosw3.execute-api.us-east-2.amazonaws.com/production/v2/sentinel-tracking/contenders'

USERS_API_URL = 'https://playoverwatch.com/en-us/search/account-by-name/%s/'

USER_AGENTS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/103.0.5060.63 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SM-A102U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12.4; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Mozilla/5.0 (Android 12; Mobile; LG-M255; rv:102.0) Gecko/102.0 Firefox/102.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 Vivaldi/4.3',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 Vivaldi/4.3',
)

COLOR_SUCCESS = Fore.GREEN
COLOR_FAILURE = Fore.RED
COLOR_NEUTRAL = Fore.CYAN
COLOR_OPTIONS = Fore.YELLOW
COLOR_EXPERIMENTAL = Fore.MAGENTA
COLOR_RESET = Fore.RESET

COLORS = (
    ('&s', COLOR_SUCCESS),
    ('&f', COLOR_FAILURE),
    ('&n', COLOR_NEUTRAL),
    ('&o', COLOR_OPTIONS),
    ('&r', COLOR_RESET)
)
