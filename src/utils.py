import json
import logging
import os
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path
from time import sleep

import requests

from constants import TMPL_LIVE_STREAM_EMBED_URL, COLORS, TMPL_LIVE_STREAM_URL, VERSION_CHECK_URL, PATH_DEBUG, \
    CURRENT_VERSION, VERSION_ENVIRON, DEBUG_ENVIRON, PATH_CONFIG, UPDATE_DOWNLOAD_URL, NOWAIT_ENVIRON, \
    DEFAULT_CHROMIUM_FLAGS, PATH_STATS


def get_version(version: str) -> tuple:
    return tuple(map(int, (version.split("."))))


def wait_before_finish(also_exit=False, exit_code=1):
    if not is_nowait():
        input('\n\nPress Enter to close...\n')
    if also_exit:
        exit(exit_code)


def get_default_config() -> dict:
    return {
        'profiles': ['default'],
        'enable_owl': True,
        'enable_owc': False,
        'headless': False,
        'shut_down': False,
        'debug': False,
        'chromium_binary': None,
        'chromium_flags': DEFAULT_CHROMIUM_FLAGS,
    }


def load_config() -> dict:
    if PATH_CONFIG.exists():
        with open(PATH_CONFIG, 'r', encoding='utf-8') as f:
            content = f.read()
            f.close()

        default_config = get_default_config()
        content = json.loads(content)
        update_config = False

        for new_flag in (
            # v2.0.2
            'chromium_binary', 'chromium_flags',

            # v2.0.5
            'shut_down',
        ):
            if new_flag not in content:
                update_config = True
                content[new_flag] = default_config[new_flag]

        if update_config:
            save_config(content)

        return content
    else:
        content = get_default_config()
        save_config(content)
        return content


def save_config(new_config: dict):
    with open(PATH_CONFIG, 'w+', encoding='utf-8') as f:
        f.write(json.dumps(new_config, indent=4))
        f.close()


def load_stats() -> list:
    content = []
    if PATH_STATS.exists():
        with open(PATH_STATS, 'r', encoding='utf-8') as f:
            content = json.loads(f.read())
            f.close()
    return content


def save_stats(new_stats: list):
    with open(PATH_STATS, 'w+', encoding='utf-8') as f:
        f.write(json.dumps(new_stats, indent=4))
        f.close()


def add_session_stats(session_stats: dict):
    stats = load_stats()
    stats.insert(0, session_stats)
    save_stats(stats)


def shut_down_pc():
    src = 'Shutdown'
    shutdown_command = []

    if sys.platform.startswith('win32'):
        shutdown_command = ['shutdown', '-s', '-t', '1']
    elif sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
        shutdown_command = ['shutdown', '-h', 'now']

    if not shutdown_command:
        log_error(src, f'Not sure how to turn off PC on platform \'{sys.platform}\'.')
        wait_before_finish(True)

    for i in reversed(range(1, 6)):
        log_info(src, f'&rThis PC will shut down in &y{i} &rsecond{"s" if i > 1 else ""}!')
        sleep(1)

    log_info(src, '&rShutting down...')
    subprocess.run(shutdown_command)


def run_powershell(command):
    subprocess.Popen(['powershell.exe', command], stdout=sys.stdout)


def kill_headless_chromes(binary_path: str | None = None):
    src = 'Ghostbuster'

    # linux: pkill -f "(chrome).*(--headless)"

    # https://superuser.com/questions/1288388/how-can-i-kill-all-headless-chrome-instances-from-the-command-line-on-windows
    if sys.platform.startswith('win32'):
        process_name = 'chrome.exe'
        if binary_path:
            process_name = binary_path.split('\\')[-1].split('/')[-1]

        log_debug(src, f'Killing stuck \'{process_name}\' processes just in case')
        try:
            run_powershell(f'Get-CimInstance Win32_Process -Filter '
                           f'"Name = \'{process_name}\' AND CommandLine LIKE \'%--headless%\'" | '
                           '%{Stop-Process $_.ProcessId}')
        except Exception as e:
            log_debug(src, f'Failed killing Chrome process(es): {str(e)}')


def get_active_stream(channel_id: str) -> str | None:
    """Returns stream url if a channel with specified channel_id has active stream"""
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
    except Exception as e:
        log_error(log_src, f'&rFailed to check for new version: {str(e)}.')
        make_debug_file('versioncheck', traceback.format_exc())
        return

    if response.status_code == 200 and get_version(latest_version) > get_version(CURRENT_VERSION):
        log_info(log_src, f'&gNew version available! You are on version &r{CURRENT_VERSION}&g, '
                          f'but version &m{latest_version}&g is available! Download here: &m{UPDATE_DOWNLOAD_URL}')
    else:
        log_info(log_src, 'No new version available!')


def is_debug() -> bool:
    return os.environ.get(DEBUG_ENVIRON, 'false') == 'true'


def set_debug(value: bool):
    os.environ.setdefault(DEBUG_ENVIRON, 'true' if value else 'false')


def is_nowait() -> bool:
    return os.environ.get(NOWAIT_ENVIRON, 'false') == 'true'


def set_nowait(value: bool):
    os.environ.setdefault(NOWAIT_ENVIRON, 'true' if value else 'false')


def make_debug_file(name: str, content: str, force: bool = False) -> Path | None:
    if is_debug() or force:
        dt = datetime.now().replace(microsecond=0).isoformat().replace(':', '-')
        filename = f'{name}_{dt}.txt'
        path = PATH_DEBUG.joinpath(filename)
        log_info('SavingDebugFile', f'Saving debug file to "{path.absolute()}" ...')
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
