import atexit
import logging
import traceback
import os
from random import randint
from time import sleep, time

from selenium.common.exceptions import WebDriverException
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

from constants import YOUTUBE_LOGIN_URL, YOUTUBE_AUTH_PASS, YOUTUBE_AUTH_FAIL, YOUTUBE_AUTH_ANY_RE, \
    OWL_CHANNEL_ID, PATH_PROFILES, OWC_CHANNEL_ID, YOUTUBE_AUTH_PASS_RE, STREAM_CHECK_FREQUENCY, NEW_TAB_URL, \
    DISCORD_URL, ISSUES_URL
from utils import log_error, log_info, log_debug, get_active_stream, is_debug, check_for_new_version, set_debug, \
    make_debug_file, get_console_message, set_nowait, wait_before_finish, kill_headless_chromes, shut_down_pc, get_seconds_till_next_match

error = lambda msg: log_error(f'Bot', msg)
info = lambda msg: log_info(f'Bot', msg)
debug = lambda msg: log_debug(f'Bot', msg)

driver_error = lambda _driver, msg: log_error(f'Chrome - \'{get_driver_profile(_driver)}\'', msg)
driver_info = lambda _driver, msg: log_info(f'Chrome - \'{get_driver_profile(_driver)}\'', msg)
driver_debug = lambda _driver, msg: log_debug(f'Chrome - \'{get_driver_profile(_driver)}\'', msg)

DRIVERS: list[uc.Chrome] = []
CURRENT_VERSION_MAIN = None


def get_driver_profile(driver: uc.Chrome) -> str:
    return getattr(driver, '__profile_name')


def get_chrome_options(config: dict) -> uc.ChromeOptions:
    options = uc.ChromeOptions()
    for argument in config['chromium_flags']:
        options.add_argument(argument)

    if config['chromium_binary']:
        options.binary_location = config['chromium_binary']

    return options


def get_driver(profile: str, config: dict) -> uc.Chrome:
    global CURRENT_VERSION_MAIN

    os.environ['WDM_LOG'] = str(logging.NOTSET)
    kwargs = {
        'options': get_chrome_options(config),
        'user_data_dir': PATH_PROFILES.joinpath(profile).absolute(),
        'headless': config['headless'],
        'log_level': 1 if is_debug() else 0,
        'version_main': CURRENT_VERSION_MAIN,
        'driver_executable_path': ChromeDriverManager().install(),
    }

    try:
        # try to create a driver with the latest ChromeDriver version
        driver = uc.Chrome(**kwargs)
    except WebDriverException as e:
        message = e.msg
        src = 'Driver'

        check_version, check_different_browser = [
            'This version of ChromeDriver only supports Chrome version' in message,
            'unrecognized Chrome version' in message,
        ]
        if check_version or check_different_browser:
            if check_version:
                log_info(src, f'ChromeDriver version differs from installed Chrome version. Trying to fix that!')

                try:
                    CURRENT_VERSION_MAIN = int(message.split('Current browser version is ')[1].rstrip().split('.')[0])
                except Exception as e:
                    log_error(src, f'Could not fix that, can\'t get correct Chrome version: {str(e)}')
                    make_debug_file('driver-version', message, True)
                    wait_before_finish()
                    exit(1)
            else:
                log_info(src, 'Unrecognized Chrome version. Are you using different browser? Trying to fix that!')

                try:
                    if 'unrecognized Chrome version: 1.0.0' in message:
                        browser, version = 'Opera', None
                        CURRENT_VERSION_MAIN = None
                        log_error('Opera is not supported, install either Google Chrome or Brave.')
                        wait_before_finish()
                        exit(1)
                    else:
                        browser_info = message.split('unrecognized Chrome version: ')[1]
                        browser, version = browser_info.split('/')
                        version_main = int(version.split('.')[0])
                        CURRENT_VERSION_MAIN = version_main

                    if browser == 'Edg':
                        log_error('MS Edge is not supported, install either Google Chrome or Brave.')
                        wait_before_finish()
                        exit(1)
                        # https://msedgewebdriverstorage.z22.web.core.windows.net/
                        # todo: if edge, use EdgeDriver instead
                except Exception as e:
                    log_error(src, f'Could not fix that, can\'t get correct Chrome version: {str(e)}')
                    make_debug_file('driver-version-other-browser', message, True)
                    wait_before_finish()
                    exit(1)

            log_info(src, f'&gSuccessfully got correct Chromium version ({CURRENT_VERSION_MAIN}) '
                          f'and browser ({browser})!')
            log_info(src, 'Trying to boot ChromeDriver with correct version instead...')

            kwargs['version_main'] = CURRENT_VERSION_MAIN
            kwargs['options'] = get_chrome_options(config)  # options can't be reused

            try:
                driver = uc.Chrome(**kwargs)
            except Exception as e:
                tb = traceback.format_exc()
                log_error(src, tb)
                print('\n')
                log_error('Could not boot your browser.')
                exit(1)

        else:
            raise e
    except TypeError as e:
        if 'expected str, bytes or os.PathLike object, not NoneType' in str(e):
            error('Can\'t find browser executable location. &ySpecify it in config.json (field "chromium_binary"). '
                  'You can get it from this url: chrome://version (search for \'Executable Path\'). '
                  'https://discord.com/channels/1103710176189628429/1103734357031653376/1104075303871062158')
            wait_before_finish()
            exit(1)
        raise e

    driver.set_window_size(1200, 800)
    setattr(driver, '__profile_name', profile)

    return driver


def watch_broadcast(driver: uc.Chrome, url: str):
    driver_info(driver, 'Driver is going to stream at ' + url + '...')
    driver.get(url)
    # todo: find a way to change quality without relying on English labels
    # driver.implicitly_wait(3)
    # setting = driver.find_element(By.CLASS_NAME, 'ytp-settings-button')
    # setting.click()
    #
    # # Click quality button
    # driver.implicitly_wait(3)
    # quality = driver.find_element(By.XPATH, '//div[@class="ytp-menuitem"]/div[text()="Quality"]')
    # quality.click()
    #
    # # Click 720p
    # sleep(0.5)
    # quality = driver.find_element_by_xpath("//span[contains(string(),'144p')]")
    # quality.click()


def start_chrome(config: dict):
    global DRIVERS, CURRENT_VERSION_MAIN

    info(f'&yBooting {len(config["profiles"])} {"headless " if config["headless"] else ""}Chrome driver(s)...')
    if not config['headless']:
        info('&yFollow all instructions you see here and &rDO NOT &ypress or '
             'do anything until asked, it may break the bot.')

    kill_headless_chromes()

    live_check_driver = get_driver('live-check', config)

    drivers = []
    for index, profile in enumerate(config['profiles']):
        drivers.append(get_driver(profile, config))
        if index == 0:
            CURRENT_VERSION_MAIN = drivers[0].patcher.version_main

    DRIVERS = drivers

    for index, driver in enumerate(drivers):
        info('&yChecking if you are logged in...')

        auth_check_time = time()
        driver.get(YOUTUBE_LOGIN_URL)

        try:
            WebDriverWait(driver, timeout=10).until(EC.url_matches(YOUTUBE_AUTH_ANY_RE))
        except WebDriverException:
            error(f'&rAuthentication check failed. You were not meant to be on URL "{driver.current_url}".')
            driver.quit()

        if driver.current_url.startswith(YOUTUBE_AUTH_FAIL):
            if config['headless']:
                driver_error(driver, '&rAuthentication check failed. '
                                     '&mPlease run this app as &rNOT headless&m and log in to your Google account.')

                for _driver in drivers:
                    _driver.quit()

                wait_before_finish()
                exit()

            else:
                driver_info(driver, '&rAuthentication check failed. '
                                    '&mPlease log in to your Google account. If you don\'t see Google\'s login screen, '
                                    'then sync your Google Chrome profile using profile button located in upper right '
                                    'corner of a browser and go manually to https://www.youtube.com/ '
                                    'Please leave your browser open for a couple of minutes after logging in to make '
                                    'sure your session persists. You have 5000 seconds for that.\n')

                WebDriverWait(driver, 5000).until(EC.url_matches(YOUTUBE_AUTH_PASS_RE))
                driver.get(NEW_TAB_URL)

        elif driver.current_url.startswith(YOUTUBE_AUTH_PASS):
            driver_info(driver, '&gAuthentication check passed.')
            driver.get(NEW_TAB_URL)

            # if not last driver, then add a little delay so Google doesn't think you are suspicious
            if index != (len(drivers) - 1) and (time() - auth_check_time) < 10:
                delay = round(time() - auth_check_time) + 1
                info(f'Looks like there are more drivers. Adding {delay} seconds delay before checking for '
                     'authentication so Google doesn\'t complain about suspicious activity.')
                sleep(delay)

    info('Setting stream status as &rOffline&y by default. Started looking for live stream...')

    live_url = None
    live_src = None
    checks_until_reload = 3
    sleep_schedule = 0

    while True:
        skip_owc_check = False

        current_url = None
        current_src = None

        info('Checking for stream status...')

        if config['enable_owl']:
            url = get_active_stream(OWL_CHANNEL_ID, live_check_driver)
            if url:
                debug('&gOWL stream is online!')
                current_url, current_src = url, 'OWL'
                skip_owc_check = True
            elif config['schedule']:
                info('Considering schedule due to stream being offline...')
                seconds = get_seconds_till_next_match()
                if seconds and seconds > 30 * 60:
                    info('Schedule approved! Bot will start checking stream manually 30 min before the scheduled match.')
                    sleep_schedule = seconds - 30 * 60
                else:
                    info('Schedule is not an option.')
                
        if config['enable_owc'] and not skip_owc_check:
            url = get_active_stream(OWC_CHANNEL_ID, live_check_driver)
            if url:
                debug('&gOWC stream is online!')
                current_url, current_src = url, 'OWC'

        if current_url != live_url:
            checks_until_reload = 3
            if current_url:
                if live_url:
                    info('Stream URL has changed?')
                else:
                    info('&gStream has just started!')

                for index, driver in enumerate(drivers):
                    watch_broadcast(driver, current_url)
                    if index != (len(drivers) - 1):
                        delay = randint(5, 15)
                        info(f'Looks like there are more drivers. Adding random {delay} seconds delay before going to '
                             f'live stream.')
                        sleep(delay)
            else:
                info('&rStream has just ended :( &cTrack your token earning progress here: '
                     'https://account.battle.net/transactions/ecosystem/1/5272175')
                for driver in drivers:
                    driver.get(NEW_TAB_URL)

                if config['shut_down']:
                    info('&rTurning this PC off... &yHit Ctrl+C to cancel!')
                    cleanup()
                    shut_down_pc()

        else:
            # nothing changed!
            if current_url:
                info('Nothing changed, stream still &gOnline&y!')

                checks_until_reload -= 1

                if checks_until_reload == 0:
                    info('Time for drivers to refresh streams...')
                    for index, driver in enumerate(drivers):
                        driver_info(driver, 'Driver is refreshing stream page...')
                        driver.refresh()
                        if index != (len(drivers) - 1):
                            delay = randint(5, 15)
                            info(f'Looks like there are more drivers. Adding random {delay} seconds '
                                 f'delay before refreshing live stream.')
                            sleep(delay)
                    checks_until_reload = 3
            else:
                info('Nothing changed, stream still &rOffline&y!')

        live_url, live_src = current_url, current_src
        if sleep_schedule:
            info(f'Bot is going to sleep for {round(sleep_schedule)} seconds due to enabled schedule option.')
            sleep(sleep_schedule)
            sleep_schedule = 0

        sleep(STREAM_CHECK_FREQUENCY + randint(0, 60))


def cleanup():
    if DRIVERS:
        log_info('Cleanup', 'Cleaning up...')
        for driver in DRIVERS:
            try:
                driver.quit()
            except:
                pass


def bootstrap(config: dict, nowait: bool = False):
    print(get_console_message(
        f'&mJoin our Discord for help, updates, suggestions, instructions and more: &g{DISCORD_URL}'
    ))

    logging.basicConfig(
        level=logging.DEBUG if config['debug'] else logging.INFO,
        format='[%(asctime)s - %(levelname)s] %(message)s'
    )

    set_debug(config['debug'])
    set_nowait(nowait)

    check_for_new_version()

    src = 'Bootstrap'

    if len(config['profiles']) == 0:
        log_error(src, 'No profiles specified!')
        wait_before_finish()
        exit(1)
    elif not any((config['enable_owl'], config['enable_owc'])):
        log_error(src, 'Enable either OWL, OWC or both!')
        wait_before_finish()
        exit(1)

    atexit.register(cleanup)
    src = 'Oops'
    first_start = time()
    last_crash = 0

    while True:
        try:
            start_chrome(config)
        except Exception as e:
            content = str(e) + '\n\n' + traceback.format_exc()

            if 'no such window: target window already closed' in content:
                log_error('Bot', 'You closed Chrome window, app can\'t work without it. '
                                 'If you don\'t want to see it, then &yenable headless mode&r in menu.')
                wait_before_finish()
                exit(1)

            path = make_debug_file('unexpected-error', content, True)

            print(content)

            log_error(src, f'\n\n&rSomething unexpected happened!\n\n'
                           f'&mFollow these steps and check if app works after each. '
                           f'These actions will fix 99% of problems.'
                           f'\n\n'
                           f'&c1. UPDATE YOUR BROWSER BY GOING TO `&gchrome://help&c`\n'
                           f'2. DELETE `&gprofiles/&c` FOLDER\n'
                           f'3. RESTART YOUR PC'
                           f'\n\n'
                           f'&rIf these steps didn\'t help, then share your issue in Discord: &y{DISCORD_URL}&r '
                           f'or open a GitHub issue: &y{ISSUES_URL}&r\n\n'
                           f'Also, please include this file: &y{str(path.absolute())}&r')

            cleanup()

            seconds_since_start = time() - first_start
            seconds_since_last_crash = time() - last_crash

            last_crash = time()

            if seconds_since_last_crash < 180:
                log_info(src, f'Won\'t try to resurrect app since '
                              f'it crashed after only {seconds_since_last_crash} seconds since last crash.')
                wait_before_finish()
                exit(1)

            if seconds_since_start < 600:
                log_info(src, f'Won\'t try to resurrect app since '
                              f'it crashed after only {seconds_since_start} seconds since start.')
                wait_before_finish()
                exit(1)

            log_info(src, 'Trying to resurrect the app...')
            continue
