import json
import logging
import os
import subprocess
import sys
import traceback
import re
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import selenium.webdriver.support.expected_conditions as EC

import requests

from constants import (
    COLORS,
    TMPL_LIVE_STREAM_URL,
    VERSION_CHECK_URL,
    PATH_DEBUG,
    CURRENT_VERSION,
    DEBUG_ENVIRON,
    PATH_CONFIG,
    UPDATE_DOWNLOAD_URL,
    NOWAIT_ENVIRON,
    DEFAULT_CHROMIUM_FLAGS,
    PATH_STATS,
    SCHEDULE_URL,
    FAKE_USER_AGENT,
    NEW_TAB_URL,
)

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
        'time_delta': False,
        'schedule': False,
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

            # v2.0.6
            'schedule',
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


def make_get_request(url: str):
    return requests.get(url, headers={'User-Agent': FAKE_USER_AGENT}, timeout=10)



def url_starts_with(url: str):
    """An expectation to check if the current url starts with a given url"""

    def _predicate(driver):
        return driver.current_url.startswith(url)

    return _predicate


def hide_chat(driver: uc.Chrome):
    try:
        chat_frame = driver.wait(seconds=5).until(
            EC.visibility_of_element_located((By.TAG_NAME, "ytd-live-chat-frame"))
        )

        if chat_frame.get_dom_attribute("collapsed") is None:
            button = driver.wait().until(
                EC.element_to_be_clickable((By.ID, "show-hide-button"))
            )
            button_text = button.text
            button.click()
            log_info("Bot", f"Clicked on '{button_text}' to hide chat window")
    except (TimeoutException, NoSuchElementException):
        pass


def check_rewards(driver: uc.Chrome):
    try:
        account_link = driver.wait(seconds=5).until(
            EC.visibility_of_element_located(
                (By.TAG_NAME, "ytd-account-link-button-renderer")
            )
        )

        # c is the curve command in svg. The check mark indicating token rewards is shown in a circle, so we must be getting rewards if the svg has curves
        svg_path = (
            account_link.find_element(By.CSS_SELECTOR, "svg>path")
            .get_attribute("d")
            .lower()
        )
        has_rewards = "c" in svg_path
        is_connected = account_link.text.strip() == "Connected"
        log_info(
            "Bot",
            f"Your account is{'' if is_connected else ' not'} connected and{'' if has_rewards else ' not'} earning rewards",
        )
    except (TimeoutException, NoSuchElementException):
        pass


def wait_for_tab(driver: uc.Chrome, tab_name: str, *args):
    args = "".join(args)
    return driver.wait().until(
        EC.presence_of_element_located(
            (By.XPATH, f'//tp-yt-paper-tab[contains(.,"{tab_name}")]{args}')
        )
    )


def videos_tab(driver: uc.Chrome):
    """click on Videos tab which contains encore streams"""
    tab = wait_for_tab(driver, "Videos")
    log_debug("Bot", "videos tab found")
    if tab.get_attribute("aria-selected") != "true":
        tab.click()
        wait_for_tab(driver, "Videos", '[@aria-selected="true"]')


def home_tab(driver: uc.Chrome):
    """wait until Home tab is selected"""
    wait_for_tab(driver, "Home", '[@aria-selected="true"]')
    log_debug("Bot", "on home tab now")


def find_live_video_url(driver: uc.Chrome):
    for open_tab in [home_tab, videos_tab]:
        open_tab(driver)
        try:
            el = driver.wait().until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "ytd-thumbnail[loaded]>a:has(div .ytd-thumbnail:is([overlay-style=LIVE]))",
                    )
                )
            )
            stream_url = el.get_attribute("href")
            log_debug("LiveCheck", f"found stream: {stream_url}")
            return stream_url
        except (TimeoutException, NoSuchElementException):
            pass

    log_info("LiveCheck", "stream not live")


def get_active_stream(channel_id: str, driver: uc.Chrome | None = None) -> str | None:
    """Returns stream url if a channel with specified channel_id has active stream"""
    src = "LiveCheck"

    check_url = "https://www.youtube.com/channel/%s" % channel_id

    try:
        if driver:
            log_debug(src, "Checking stream status using WebDriver...")
            driver.get(check_url)
            if "consent.youtube.com" in driver.current_url:
                log_debug(src, "YouTube asked for consent")
                try:
                    element = driver.find_element(
                        By.XPATH, '//form[@action="https://consent.youtube.com/save"]'
                    )
                    element.click()
                except:
                    log_error(src, "Failed to get stream status using driver!")
                    return

            driver.wait().until(
                url_starts_with("https://www.youtube.com/")
            )
            stream_url = find_live_video_url(driver)
            driver.get(NEW_TAB_URL)
            return stream_url

        if not driver:
            log_debug(src, "Checking stream status using 'requests'...")
            response = make_get_request(check_url).text

            matches = re.search(r"/([\w-]+)/hqdefault_live.jpg", response)
            if matches is not None and len(matches.groups()) > 0:
                video_id = matches.group(1)
                return TMPL_LIVE_STREAM_URL % video_id

    except Exception as e:
        log_error(src, f"&rLive stream check failed: {str(e)}")
        make_debug_file("failed-getting-active-stream", traceback.format_exc())
        return



def get_seconds_till_next_match() -> float | None:
    src = 'Schedule'

    try:
        # getting page json
        schedule_html = make_get_request(SCHEDULE_URL).text
        next_data = (
            schedule_html
            .split('<script id="__NEXT_DATA__" type="application/json">')[1]
            .split('</script>')[0].strip()
        )
        schedule_json = json.loads(next_data)

        # getting matches
        blocks = schedule_json['props']['pageProps']['blocks']
        matches: list = []
        for block in blocks:
            if 'owlHeader' in block.keys():
                matches = block['owlHeader']['scoreStripList']['scoreStrip']['matches']
                break

        if not matches:
            raise Exception('Could not get matches.')

        pending_matches = list(filter(lambda match: match.get('status') == 'PENDING', matches))
        pending_matches.sort(key=lambda match: match['date']['startDate'])

        if not pending_matches:
            raise Exception(f"No matches with status 'PENDING'.")

        timestamp_ms = pending_matches[0]['date']['startDate']
        delta = datetime.fromtimestamp(timestamp_ms / 1000, timezone.utc) - datetime.now(timezone.utc)
        total_seconds = delta.total_seconds()

        log_info(src, f'Closest match will be played in {delta}.')

        return total_seconds
    except Exception as e:
        log_error(src, f'&rSchedule check failed: {str(e)}. Falling back to regular checks.')
        make_debug_file('failed-getting-schedule', traceback.format_exc())


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
