import asyncio
import json
import logging
import random
from datetime import datetime

import aiohttp

from constants import COLORS, USER_AGENTS


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
    async def post(session, url, payload: dict, headers: dict):
        # first mimic options request
        async with session.options(url, headers=headers) as response:
            await response.read()

        # then do actual request
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status != 200:
                raise Exception('Status not 200.')
            response_json = await response.json()
            return response_json

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
        payloads = [(self.get_request_payload(account_id), get_headers(account_id)) for account_id in self.account_ids]
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(*[
                self.post(session, self.track_url, payload=payload, headers=headers) for payload, headers in payloads
            ], return_exceptions=True)

            total_count = len(results)
            success_count = len([i for i in results if isinstance(i, dict)])

            if total_count == 1:
                if success_count:
                    self.log(f'&sSuccess.&r Time successfully tracked!')
                else:
                    self.log(f'&fFailure.&r Time-tracking request was unsuccessful.')

            else:
                self.log(f'&n{success_count}&r of &n{total_count}&r tracking requests were successful.')

    def get_request_payload(self, account_id: int):
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

    async def get_next_data(self):
        async with aiohttp.ClientSession(headers=get_headers(self.account_ids[0])) as session:
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

        data = await self.get_next_data()
        data_player = [i['videoPlayer'] for i in data['props']['pageProps']['blocks'] if 'videoPlayer' in i][0]

        was_live = self.is_live
        self.entry_id = data_player['uid']

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
        status = ('&sLive' if self.is_live else '&fNot Live') + '&r'
        return status

    def log(self, text: str):
        text = f'&n({self.prefix})&r {text}'
        for color_code, color in COLORS:
            text = text.replace(color_code, color)
        logging.info(text)
