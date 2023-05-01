import atexit
import logging
from random import randint
from time import sleep, time

from selenium.common.exceptions import WebDriverException
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc

from constants import YOUTUBE_LOGIN_URL, YOUTUBE_AUTH_PASS, YOUTUBE_AUTH_FAIL, YOUTUBE_AUTH_ANY_RE, \
    OWL_CHANNEL_ID, PATH_PROFILES, OWC_CHANNEL_ID, YOUTUBE_AUTH_PASS_RE, STREAM_CHECK_FREQUENCY, NEW_TAB_URL
from utils import log_error, log_info, log_debug, get_active_stream, is_debug, check_for_new_version, set_debug


error = lambda msg: log_error(f'Bot', msg)
info = lambda msg: log_info(f'Bot', msg)
debug = lambda msg: log_debug(f'Bot', msg)

driver_error = lambda _driver, msg: log_error(f'Chrome - \'{get_driver_profile(_driver)}\'', msg)
driver_info = lambda _driver, msg: log_error(f'Chrome - \'{get_driver_profile(_driver)}\'', msg)
driver_debug = lambda _driver, msg: log_error(f'Chrome - \'{get_driver_profile(_driver)}\'', msg)

DRIVERS: list[uc.Chrome] = []


def get_driver_profile(driver: uc.Chrome) -> str:
    return getattr(driver, '__profile_name')


def get_driver(profile: str, is_headless: bool) -> uc.Chrome:
    options = uc.ChromeOptions()
    options.add_argument('--autoplay-policy=no-user-gesture-required')
    options.add_argument('--disable-extensions')
    options.add_argument('--mute-audio')
    driver = uc.Chrome(
        options=options,
        user_data_dir=PATH_PROFILES.joinpath(profile).absolute(),
        headless=is_headless,
        log_level=3 if is_debug() else 0,
    )
    driver.set_window_size(1200, 800)

    setattr(driver, '__profile_name', profile)

    return driver


def watch_broadcast(driver: uc.Chrome, url: str):
    driver_debug(driver, 'Driver is going to stream at ' + url + '...')
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


def start_chrome(profiles: list[str], is_headless: bool, check_owl: bool, check_owc: bool):
    global DRIVERS

    info(f'&yBooting {len(profiles)} {"headless " if is_headless else ""}Chrome driver(s)...')
    info('&yFollow all instructions you see here and &rDO NOT &ypress or '
         'do anything until asked, it may break the bot.')

    drivers = [get_driver(profile, is_headless) for profile in profiles]
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
            if is_headless:
                driver_error(driver, '&rAuthentication check failed. '
                                     '&mPlease run this app as &rNOT headless&m and log in to your Google account.')

                for _driver in drivers:
                    _driver.quit()

                exit()

            else:
                driver_info(driver, '&rAuthentication check failed. '
                                    '&mPlease log in to your Google account. If you don\'t see Google\'s login screen, '
                                    'then go to https://gmail.com/ and log in there and then go to '
                                    'https://youtube.com/. You have 5000 seconds for this.')

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

    info('Started looking for live stream...')

    live_url = None
    live_src = None

    while True:
        skip_owc_check = False

        current_url = None
        current_src = None

        debug('Checking for stream status...')

        if check_owl:
            url = get_active_stream(OWL_CHANNEL_ID)
            if url:
                debug('OWL stream is online!')
                current_url, current_src = url, 'OWL'
                skip_owc_check = True

        if check_owc and not skip_owc_check:
            url = get_active_stream(OWC_CHANNEL_ID)
            if url:
                debug('OWC stream is online!')
                current_url, current_src = url, 'OWC'

        if current_url != live_url:
            if current_url:
                if live_url:
                    info('Stream URL has changed?')
                else:
                    info('Stream has just started!')

                for index, driver in enumerate(drivers):
                    watch_broadcast(driver, current_url)
                    if index != (len(drivers) - 1):
                        delay = randint(5, 15)
                        debug(f'Looks like there are more drivers. Adding random {delay} seconds delay before going to '
                              f'live stream so Google doesn\'t complain about suspicious activity.')
                        sleep(delay)
            else:
                info('Stream has just ended :(')
                for driver in drivers:
                    driver.get(NEW_TAB_URL)
        else:
            # nothing changed!
            pass

        live_url, live_src = current_url, current_src
        sleep(STREAM_CHECK_FREQUENCY)


def cleanup():
    for driver in DRIVERS:
        try:
            driver.quit()
        except:
            pass
    print('Bye!')


def bootstrap(config: dict):
    logging.basicConfig(
        level=logging.DEBUG if config['debug'] else logging.INFO,
        format='[%(asctime)s - %(levelname)s] %(message)s'
    )

    set_debug(config['debug'])

    check_for_new_version()

    src = 'Bootstrap'

    if len(config['profiles']) == 0:
        log_error(src, 'No profiles specified!')
        exit()
    elif not any((config['enable_owl'], config['enable_owc'])):
        log_error(src, 'Enable either OWL, OWC or both!')
        exit()

    atexit.register(cleanup)

    start_chrome(
        profiles=config['profiles'],
        is_headless=config['headless'],
        check_owl=config['enable_owl'],
        check_owc=config['enable_owc']
    )
