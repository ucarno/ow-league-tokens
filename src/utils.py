import json
import logging
import os
import traceback
from datetime import datetime
from pathlib import Path

import requests

from constants import TMPL_LIVE_STREAM_EMBED_URL, COLORS, TMPL_LIVE_STREAM_URL, VERSION_CHECK_URL, PATH_DEBUG, \
    CURRENT_VERSION, VERSION_ENVIRON, DEBUG_ENVIRON, PATH_CONFIG, UPDATE_DOWNLOAD_URL


def load_config() -> dict:
    if PATH_CONFIG.exists():
        with open(PATH_CONFIG, 'r', encoding='utf-8') as f:
            content = f.read()
            f.close()
        return json.loads(content)
    else:
        return {
            'profiles': ['default'],
            'enable_owl': True,
            'enable_owc': False,
            'headless': False,
            'debug': False,
        }


def save_config(new_config: dict):
    with open(PATH_CONFIG, 'w+', encoding='utf-8') as f:
        f.write(json.dumps(new_config, indent=4))
        f.close()


def get_active_stream(channel_id: str) -> str | None:
    """Returns stream url if channel with specified channel_id has active stream"""
    debug = is_debug()
    src = 'LiveCheck'

    try:
        response = requests.get(TMPL_LIVE_STREAM_EMBED_URL % channel_id, timeout=10).text
    except requests.RequestException as e:
        log_error(src, f'&rLive stream check failed: {str(e)}')
        tb = traceback.format_exc()
        make_debug_file('failed-getting-active-stream', tb)
        return

    try:
        response_data = json.loads(response.split('ytcfg.set(')[1].split(');window.ytcfg.obfuscatedData_')[0])
    except (IndexError, json.JSONDecodeError) as e:
        log_error(src, '&rFailed parsing live stream data from YouTube embed...')
        make_debug_file('livecheck_parsing', response)
        return

    try:
        player_data = response_data['PLAYER_VARS']
    except KeyError:
        log_error(src, 'Could not access "PLAYER_VARS". Trying to get ID using another method...')

        make_debug_file('livecheck_status', json.dumps(response_data))

        try:
            video_id = response_data['VIDEO_ID']
            log_info(src, 'Got video ID using another method! '
                          'But not sure whether it is a live stream or just video...')
            return TMPL_LIVE_STREAM_URL % video_id
        except KeyError:
            log_error(src, 'Could not get live stream video id.')
            return

    try:
        video_id = player_data['video_id']
        embedded_player_response = json.loads(player_data['embedded_player_response'])

        if embedded_player_response['previewPlayabilityStatus']['status'] == 'OK':
            return TMPL_LIVE_STREAM_URL % video_id
    except KeyError as e:
        log_error(src, f'Could not get stream status: {str(e)}.')
        make_debug_file('livecheck_general', traceback.format_exc() + '\n\n' + json.dumps(player_data))


def check_for_new_version():
    log_src = 'Version'
    log_info(log_src, 'Checking for new version...')
    try:
        response = requests.get(VERSION_CHECK_URL, timeout=3)
        latest_version = response.text.strip()
    except requests.RequestException as e:
        log_error(log_src, f'&rFailed to check for new version: {str(e)}.')
        make_debug_file('versioncheck', traceback.format_exc())
        return

    if response.status_code == 200 and latest_version != CURRENT_VERSION:
        log_info(log_src, f'&gNew version available! You are on version &r{CURRENT_VERSION}&g, '
                          f'but version &m{latest_version}&g is available! Download here: &m{UPDATE_DOWNLOAD_URL}')
        os.environ.setdefault(VERSION_ENVIRON, 'true')
    else:
        log_info(log_src, 'No new version available!')
        os.environ.setdefault(VERSION_ENVIRON, 'false')


def is_debug() -> bool:
    return os.environ.get(DEBUG_ENVIRON, 'false') == 'true'


def set_debug(value: bool):
    os.environ.setdefault(DEBUG_ENVIRON, 'true' if value else 'false')


def make_debug_file(name: str, content: str) -> Path | None:
    if is_debug():
        dt = datetime.now().replace(microsecond=0).isoformat().replace(':', '-')
        filename = f'{name}_{dt}.txt'
        path = PATH_DEBUG.joinpath(filename)
        log_debug('SavingDebugFile', f'Saving debug file to "{path.absolute()}" ...')
        with open(path, 'w+', encoding='utf-8') as f:
            f.write(content)
            f.close()
        return path


def get_console_message(message: str):
    message = message + '&!r'
    for color_code, color in COLORS:
        message = message.replace(color_code, color)
    return message


log_error = lambda src, msg: logging.error(get_console_message(f'&c({src})&r ' + msg + '&!r'))
log_info = lambda src, msg: logging.info(get_console_message(f'&c({src})&y ' + msg + '&!r'))
log_debug = lambda src, msg: logging.debug(get_console_message(f'&c({src})&y ' + msg + '&!r'))
