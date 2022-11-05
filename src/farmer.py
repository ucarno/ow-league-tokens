import asyncio
import json
import logging
import random
from datetime import datetime
from json import JSONDecodeError

import aiohttp
from aiohttp import ClientTimeout, ClientConnectionError

from constants import USER_AGENTS
from utils import format_text


def get_headers(account_id: int):
    random.seed(account_id)
    return {
        'accept-language': 'en-US,en;q=1.0',
        'origin': 'https://overwatchleague.com',
        'referer': 'https://overwatchleague.com/',
        'x-origin': 'overwatchleague.com',
        'user-agent': random.choice(USER_AGENTS)
    }


class Farmer:
    def __init__(
            self, prefix: str, check_url: str, track_url: str, account_ids: list[int],
            check_if_live: bool = False, check_sentinel: bool = False
    ):
        self.prefix = prefix

        self.check_if_live = check_if_live
        self.check_sentinel = check_sentinel

        self.check_url = check_url
        self.track_url = track_url

        self.account_ids = account_ids

        self.is_live = False
        self.video_id = None
        self.entry_id = None

        self.tasks = []

    @staticmethod
    async def post(session, url, payload: dict, headers: dict, account_id: int) -> tuple[int, dict]:
        # first mimic options request
        async with session.options(url, headers=headers) as response:
            await response.read()

        # then do actual request
        async with session.post(url, json=payload, headers=headers) as response:
            response_json = await response.json()
            if response.status != 200 or response_json['status'] != 200:
                raise Exception(f'&rStatus {response.status} (Account ID: &n{account_id}&r; Response: &n{response_json}&r)')
            return account_id, response_json

    async def track_loop(self):
        while True:
            if self.is_live:
                asyncio.create_task(self.track_watching())
            await asyncio.sleep(60)

    async def update_loop(self):
        while True:
            asyncio.create_task(self.update_data())
            await asyncio.sleep(3*60)

    async def track_watching(self):
        self.log('Sending time-tracking request(s)...')
        payloads = [
            (self.get_request_payload(account_id), get_headers(account_id), account_id) for account_id in
            self.account_ids
        ]
        async with aiohttp.ClientSession(timeout=ClientTimeout(total=10)) as session:
            results = await asyncio.gather(*[
                self.post(
                    session=session,
                    url=self.track_url,
                    payload=payload,
                    headers=headers,
                    account_id=account_id
                ) for payload, headers, account_id in payloads
            ], return_exceptions=True)

            total_count = len(results)
            success_count = len([i for i in results if not isinstance(i, Exception)])

            if total_count == 1:
                if success_count:
                    self.log('&sSuccess.&r Time successfully tracked!')
                else:
                    self.log('&fFailure.&r Time-tracking request was unsuccessful.')

            else:
                self.log(f'&n{success_count}&r of &n{total_count}&r tracking requests were successful.')

            request_responses = []
            for r in results:
                if isinstance(r, Exception):
                    request_responses.append(f'&fFailure&r: {r.__class__.__name__} -> {str(r)}')
                else:
                    account_id, response_json = r
                    request_responses.append(f'&sSuccess&r: Status 200 (Account ID: &n{account_id}&r; Response: &n{response_json}&r)')

            for i, r in enumerate(request_responses):
                self.debug(f'  ({i+1}) {r}')

    def get_request_payload(self, account_id: int) -> dict:
        return {
            'accountId': str(account_id),
            'entryId': self.entry_id,
            'liveTest': False,
            'locale': 'en-us',
            'type': 'video_player',
            'videoId': self.video_id,
            'timestamp': datetime.now().timestamp(),
            'contentType': 'live',
            'id_type': 'battleNetId'
        }

    async def get_next_data(self) -> dict:
        async with aiohttp.ClientSession(
            headers=get_headers(self.account_ids[0]),
            timeout=ClientTimeout(total=10)
        ) as session:
            async with session.get(self.check_url) as response:
                html = await response.text()
                json_text = (
                    html
                    .split('<script id="__NEXT_DATA__" type="application/json">')[1]
                    .split('</script>')[0]
                )
                return json.loads(json_text)

    async def update_data(self):
        self.log('Updating stream status...')

        try:
            data = await self.get_next_data()
        except ClientConnectionError as e:
            self.log(f'&fCould not connect to OWL website, keeping stream status as {self.status}&f.&r')
            self.debug(f'{e.__class__.__name__} -> {str(e)}')
            return
        except (IndexError, JSONDecodeError) as e:
            self.log(f'&fCould not gather or decode NEXT data, keeping stream status as {self.status}&f.&r')
            self.debug(f'{e.__class__.__name__} -> {str(e)}')
            return
        except Exception as e:
            self.log(f'&fCould not update data, keeping stream status as {self.status}&f.&r')
            self.debug(f'{e.__class__.__name__} -> {str(e)}')
            return

        try:
            data_player = [i['videoPlayer'] for i in data['props']['pageProps']['blocks'] if 'videoPlayer' in i][0]
        except (IndexError, KeyError) as e:
            self.log(f'&fCould not get player data, keeping stream status as {self.status}&f.&r')
            self.debug(f'{e.__class__.__name__} -> {str(e)}')
            return

        was_live = self.is_live

        try:
            self.entry_id = data_player['uid']
        except KeyError:
            if was_live:
                self.log(f'&fCould not get player \'uid\', which is necessary'
                         'for bot to track time, trying to leave everything as is.&r')
            return

        sentinel_passed = True
        if self.check_sentinel:
            try:
                sentinel_passed = data_player['videoLogin'][0]['enableSentinelTracking'] == 'None'
            except (KeyError, IndexError, TypeError):
                sentinel_passed = False

        try:
            is_live_check = data_player['video']['isLive'] if self.check_if_live else True
            self.video_id = data_player['video']['id']
            self.is_live = bool(self.video_id) and sentinel_passed and is_live_check
        except (KeyError, TypeError):
            self.video_id = None
            self.is_live = False

        if was_live == self.is_live:
            self.log(f'Nothing changed. Stream is still {self.status}.')
        else:
            self.log(f'Stream status changed. Stream is now {self.status}.')

    async def run(self):
        self.tasks.append(asyncio.create_task(self.update_loop()))
        await asyncio.sleep(3)
        self.tasks.append(asyncio.create_task(self.track_loop()))

    @property
    def status(self) -> str:
        status = ('&sLive' if self.is_live else '&fOffline') + '&r'
        return status

    def format_text(self, text: str):
        return format_text(f'&n({self.prefix})&r {text}')

    def log(self, text: str):
        logging.info(self.format_text(text))

    def debug(self, text: str):
        logging.debug(self.format_text(text))
