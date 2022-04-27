import json
from datetime import datetime
from threading import Thread
from time import sleep

import requests
from colorama import Fore, init


LEAGUE_URL = 'https://overwatchleague.com/en-us/'
TRACK_URL = 'https://wzavfvwgfk.execute-api.us-east-2.amazonaws.com/production/v2/sentinel-tracking/owl'
USERS_API_URL = 'https://playoverwatch.com/en-us/search/account-by-name/%s/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'
HEADERS = {
    'accept-language': 'en-US,en;q=1.0',
    'origin': 'https://overwatchleague.com',
    'referer': 'https://overwatchleague.com/',
    'x-origin': 'overwatchleague.com',
    'user-agent': USER_AGENT
}


success = Fore.GREEN
failure = Fore.RED


class Farmer:
    def __init__(self, account_id: int):
        self.account_id = int(account_id)

        self.is_live = False
        self.video_id = None
        self.entry_id = None

        self._continue = True

    def updater_loop(self):
        while True:
            sleep(3*60)
            Thread(target=self.update_data).start()

    def tracker_loop(self):
        while True:
            if not self._continue:
                sleep(3*60)
                self._continue = True
            if self.is_live:
                Thread(target=self.track_watching).start()
            sleep(1*60)

    def start(self):
        self.log(f'Farmer started. Setting stream status to {self.status}.')
        self.update_data()
        updater_thread = Thread(target=self.updater_loop)
        tracker_thread = Thread(target=self.tracker_loop)

        updater_thread.start()
        sleep(5)
        tracker_thread.start()

    @property
    def status(self) -> str:
        status = ((success + 'Live') if self.is_live else (failure + 'Not Live')) + Fore.RESET
        return status

    @staticmethod
    def get_next_data():
        html = requests.get(LEAGUE_URL, headers=HEADERS).text
        json_text = (
            html
            .split('<script id="__NEXT_DATA__" type="application/json">')[1]
            .split('</script>')[0]
        )
        return json.loads(json_text)

    def update_data(self):
        self.log('Updating stream status...')

        data = self.get_next_data()
        data_player = [i['videoPlayer'] for i in data['props']['pageProps']['blocks'] if i.get('videoPlayer')][0]
        # data_match = [i['matchTicker'] for i in data['props']['pageProps']['blocks'] if i.get('matchTicker')][0]

        was_live = self.is_live
        self.entry_id = data_player['uid']

        # try:
        #     self.video_id = data_player['video']['id']
        #     self.is_live = data_match['status'] == 'IN_PROGRESS' or data_match['timeToMatch'] == 0
        # except (KeyError, TypeError):
        #     self.video_id = None
        #     self.is_live = False

        try:
            self.video_id = data_player['video']['id']
            self.is_live = bool(self.video_id)
        except (KeyError, TypeError):
            self.video_id = None
            self.is_live = False

        if was_live == self.is_live:
            self.log(f'Nothing changed. Stream is still {self.status}.')
        else:
            self.log(f'Stream status changed. Stream is now {self.status}.')

    def get_request_payload(self):
        return {
            'accountId': str(self.account_id),
            'entryId': self.entry_id,
            'liveTest': False,
            'locale': 'en-us',
            'type': 'video_player',
            'videoId': self.video_id,
        }

    def track_watching(self):
        self.log('Sending time-tracking request...')
        post = requests.post(
            url=TRACK_URL,
            headers=HEADERS,
            json=self.get_request_payload()
        )
        options = requests.options(
            url=TRACK_URL,
            headers=HEADERS
        )

        try:
            response = json.loads(post.text)
            self._continue = response['data']['continueTracking']
        except (KeyError, TypeError):
            self._continue = False

        if post.status_code == 200:
            self.log(f'{success}Success.{Fore.RESET} Time successfully tracked!')
        else:
            self.log(f'{failure}Failure.{Fore.RESET} Time-tracking request was unsuccessful.')

    @staticmethod
    def log(text: str):
        time = datetime.now().strftime('%H:%M:%S')
        print(f'[{time}] {text}')


if __name__ == '__main__':
    init()

    try:
        config = json.loads(open('config.json', 'r', encoding='utf-8').read())
    except FileNotFoundError:
        config = {'account_id': None}

    if not config['account_id']:
        print('It looks like it is the first time you launch this program!')
        while True:
            print(f'What is your username? (for example {Fore.YELLOW}myUsername{Fore.RESET} '
                  f'or {Fore.YELLOW}myUsername#1234{Fore.RESET})')
            username = input(' > ')
            if not username:
                print(Fore.RED + 'Incorrect username.', end='\n\n')
                continue

            url = USERS_API_URL % (username.replace('#', '%23'),)
            users = json.loads(requests.get(url).text)
            if not users:
                print(Fore.RED + 'Users with that username not found.' + Fore.RESET, end='\n\n')
                continue

            if len(users) == 1:
                user_dict = users[0]
            else:
                print(f'Found {len(users)} users with that username. You are..?')
                for index, item in enumerate(users):
                    print(f' {index+1}. {item["name"]} (level: {item["playerLevel"]}, platform {item["platform"].upper()})')
                while True:
                    number = input(' > ')
                    if not number.isdigit() or int(number)-1 not in range(len(users)):
                        print(f'{Fore.RED}Invalid number.{Fore.RESET}')
                        continue
                    user_dict = users[int(number)-1]
                    break

            aid = user_dict['id']
            config['account_id'] = aid
            with open('config.json', 'w+', encoding='utf-8') as f:
                f.write(json.dumps(config))
                f.close()

            print(success + 'Configuration successful!' + Fore.RESET, end='\n\n')
            break

    farmer = Farmer(**config)
    farmer.start()
