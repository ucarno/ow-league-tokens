import logging
import queue
from threading import Thread
from time import sleep

from selenium.common.exceptions import WebDriverException
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc

from constants import YOUTUBE_LOGIN_URL, YOUTUBE_AUTH_PASS, YOUTUBE_AUTH_FAIL, YOUTUBE_AUTH_ANY_RE, \
    OWL_CHANNEL_ID, PATH_PROFILES, OWC_CHANNEL_ID, YOUTUBE_AUTH_PASS_RE
from utils import log_error, log_info, log_debug, kill, get_active_stream, is_debug

KILL_SENTINEL = object()


def start_chrome(profile_name: str, is_owl: bool, is_headless: bool, q: queue.Queue):
    league_src = 'OWL' if is_owl else 'OWC'

    error = lambda msg: log_error(f'Chrome - {profile_name} - {league_src}', msg)
    info = lambda msg: log_info(f'Chrome - {profile_name} - {league_src}', msg)
    debug = lambda msg: log_debug(f'Chrome - {profile_name} - {league_src}', msg)

    info(f'&yBooting {"headless " if is_headless else ""}Chrome...')
    info('&yFollow all instructions you see here and &rDO NOT &ypress or do anything until asked, it may break the bot.')

    options = uc.ChromeOptions()
    options.add_argument('--autoplay-policy=no-user-gesture-required')
    options.add_argument('--disable-extensions')
    options.add_argument("--mute-audio")
    driver = uc.Chrome(
        options=options,
        user_data_dir=PATH_PROFILES.joinpath(profile_name).absolute(),
        headless=is_headless,
        log_level=3 if is_debug() else 0,
    )
    driver.set_window_size(1200, 800)

    info('&yChecking if you are logged in...')
    driver.get(YOUTUBE_LOGIN_URL)

    try:
        WebDriverWait(driver, timeout=10).until(EC.url_matches(YOUTUBE_AUTH_ANY_RE))
    except WebDriverException:
        error(f'&rAuthentication check failed. You were not meant to be on URL "{driver.current_url}".')
        driver.close()
        kill()

    if driver.current_url.startswith(YOUTUBE_AUTH_FAIL):
        if is_headless:
            info('&rAuthentication check failed. '
                 '&mPlease run this app as &rNOT headless&m and log in to your Google account.')
            kill()
        else:
            info('&rAuthentication check failed. '
                 '&mPlease log in to your Google account.')

            WebDriverWait(driver, 5000).until(EC.url_matches(YOUTUBE_AUTH_PASS_RE))

    elif driver.current_url.startswith(YOUTUBE_AUTH_PASS):
        info('&gAuthentication check passed.')

    info('Started looking for live stream...')

    while True:
        item = q.get()
        if item == KILL_SENTINEL:
            info('Received kill signal...')
            driver.close()
            kill()  # todo: rewrite to exit to close all drivers
        elif not item:
            driver.get('chrome://new-tab-page/')
        else:
            info(f'Received new stream URL! Going to {item}...')
            driver.get(item)
            info('Watching stream!')

            # todo: find another way to change quality
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


def start_watchdog(is_owl: bool, queues: list[queue.Queue, ...]):
    src = 'OWL' if is_owl else 'OWC'
    channel_id = OWL_CHANNEL_ID if is_owl else OWC_CHANNEL_ID

    error = lambda msg: log_error(f'Watchdog - {src}', msg)
    info = lambda msg: log_info(f'Watchdog - {src}', msg)
    debug = lambda msg: log_debug(f'Watchdog - {src}', msg)

    last_stream: str | None = None

    while True:
        info('&yChecking if live stream is available...')
        current_stream = get_active_stream(channel_id)
        if last_stream == current_stream:
            info('&yNothing changed...')
            sleep(60)
            continue

        if current_stream:
            # stream just started or stream url has changed
            if last_stream:
                # stream url has changed
                info('&yStream URL has changed.')
            else:
                # stream just started
                info('&yStream is now &gLive&y!')
        else:
            # stream ended :(
            info('&yStream is now &rOffline&y.')

        last_stream = current_stream
        for q in queues:
            q.put(current_stream)
        sleep(60)


def bootstrap(config: dict):
    logging.basicConfig(
        level=logging.DEBUG if config['debug'] else logging.INFO,
        format='[%(asctime)s - %(levelname)s] %(message)s'
    )

    threads = []

    profiles = config['profiles']
    owl = config['enable_owl']
    owc = config['enable_owc']
    is_headless = config['headless']

    log_src = 'Bootstrap'

    if len(profiles) == 0:
        log_error(log_src, 'No profiles specified!')
        exit()
    elif not owl and not owc:
        log_error(log_src, 'Enable either OWL, OWC or both!')
        exit()

    if owl:
        queues = [queue.Queue() for _ in profiles]
        threads.append(Thread(target=start_watchdog, args=(True, queues)))
        for index, profile in enumerate(profiles):
            threads.append(Thread(target=start_chrome, args=(profile, True, is_headless, queues[index])))

    if owc:
        queues = [queue.Queue() for _ in profiles]
        threads.append(Thread(target=start_watchdog, args=(False, queues)))
        for index, profile in enumerate(profiles):
            threads.append(Thread(target=start_chrome, args=(profile, False, is_headless, queues[index])))

    for thread in threads:
        thread.start()
