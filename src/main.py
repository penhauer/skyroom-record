from distutils.command.config import config
from ntpath import join
import os
from pkgutil import extend_path
from cv2 import RETR_LIST
import pyautogui
import time
import math
import cv2
import numpy as np
import ffmpeg
import argparse
import logging

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import ui
from skimage.metrics import structural_similarity as ssim
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

pyautogui.FAILSAFE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FAILURE_TEST_INTERVAL = timedelta(minutes=5)
SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(SOURCE_DIR)


def split_to_100bulks(arr):
    result = []
    for i in range(math.ceil(len(arr) / 100)):
        result.append(arr[i * 100:(i + 1) * 100])
    return result


def goto_class(driver):
    driver.find_element_by_id('btn_guest').click()


def force_refresh(driver):
    driver.execute_script('window.onbeforeunload = function() {};')
    time.sleep(0.5)
    driver.refresh()


def is_need_recording():
    return not os.path.exists('./force-stop-recording')


def click_on_image(image_path):
    img_location = pyautogui.locateOnScreen(image_path, confidence=0.70)
    image_location_point = pyautogui.center(img_location)
    x, y = image_location_point
    pyautogui.click(x, y)


def click_on_point(x, y):
    pyautogui.click(x, y)


def start_recording_with_screen_recorder(driver):
    time.sleep(0.5)
    # click_on_image(os.path.join(SOURCE_DIR, "Icons/Extensions.png")) # click to see the extensions pop up
    click_on_point(1800, 50)
    time.sleep(0.5)
    # click_on_image(os.path.join(SOURCE_DIR, "Icons/screen_recorder_old.png")) # click screen recorder from extensions pop up
    click_on_point(1550, 205)
    time.sleep(0.5)

    driver.switch_to.window(driver.window_handles[1])
    driver.maximize_window()

    driver.find_element_by_xpath('//*[@id="root"]/div[4]/div[3]/div[3]/div/main/div/div[1]/button').click()
    time.sleep(0.5)
    driver.find_element_by_xpath('//*[@id="root"]/div[4]/div[3]/div[6]/div/main/div/div[4]/button').click()
    time.sleep(0.5)
    driver.find_element_by_xpath('//*[@id="root"]/div[4]/div[4]/button').click()
    time.sleep(0.5)

    click_on_point(1200, 90)
    time.sleep(0.2)
    click_on_point(800, 150)
    time.sleep(0.2)
    click_on_point(1200, 460)
    time.sleep(0.2)


def configure_parser():
    parser = argparse.ArgumentParser(
        description='This command will record a VClass page')
    parser.add_argument('-u', '--url', type=str,
                        default='', help='URL of vclass')
    parser.add_argument('-d', '--duration', type=float,
                        default=0, help='Duration of class in minutes')
    parser.add_argument('-n', '--name', type=str,
                        default='', help='Name of downloads folder')
    parser.add_argument('-a', '--username', type=str,
                        default='ضبط کننده', help='Username of skyroom user')
    parser.add_argument('-e', '--encoding', type=str,
                        default='no-encode',
                        help='Encoding quality, see readme.md')
    parser.add_argument('-v', '--video', type=str,
                        default='',
                        help='Video to encode')
    parser.add_argument('--debug', help="enable debug mode", 
                        action='store_true')
    return parser


def start_driver(download_path):
    os.mkdir(download_path)
    chrome_options = Options()
    extension_path = os.path.join(SOURCE_DIR, 'Extensions/OldScreenRecorder')
    chrome_options.add_argument(f"--load-extension={extension_path}")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("disable-infobars")

    logger.info('Starting driver...')
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    time.sleep(0.5)
    driver.maximize_window()
    return driver


def create_downloads_folder_if_not_exists(args):
    try:
        os.mkdir(os.path.join(BASE_DIR, 'downloads', args.name))
    except FileExistsError:
        pass


def close_all_other_windows(driver):
        main_window = driver.current_window_handle
        handles = driver.window_handles.copy()
        for handle in handles:
            if not handle == main_window:
                driver.switch_to.window(handle)
                driver.close()
        driver.switch_to.window(main_window)


def open_url(driver, url):
    driver.get(url)


def try_catch(f, args):
    RETRIES = 5
    for retry_number in range(RETRIES):
        try:
            time.sleep(retry_number)
            logger.info(f"trying to {f} for {retry_number}th time")
            f(*args)
            break
        except Exception as e:
            logger.exception(e)
            if retry_number + 1 == RETRIES:
                raise e


def login(driver, args):
    force_refresh(driver)
    time.sleep(3)
    goto_class(driver)
    driver.find_element_by_xpath("//input[@class='full-width']")
    driver.execute_script(
        "document.querySelector('.dlg-nickname .full-width').value"
        f" = '{args.username}';")
    driver.execute_script(
        "document.querySelector('.dlg-nickname .btn').click();")


def stop_recordering(driver):
    driver.find_element_by_xpath('//*[@id="root"]/div[4]/div[4]/button[1]').click()
    time.sleep(0.3)
    driver.find_element_by_xpath('//*[@id="root"]/div[4]/div[2]/div/div[1]/button').click()
    time.sleep(0.3)
    driver.find_element_by_xpath('//*[@id="root"]/div[4]/div[4]/button[1]').click()

def close_all_windows(driver):
    handles = driver.window_handles.copy()
    for window_handle in handles:
        driver.switch_to.window(window_handle)
        driver.close()

def record_video(args):
    create_downloads_folder_if_not_exists(args)

    download_path = os.path.join(BASE_DIR, 'downloads', args.name, datetime.now().strftime("%Y-%m-%d--%H-%M"))
    driver = start_driver(download_path)

    close_all_other_windows(driver)

    logger.info('opening url...')
    try_catch(open_url, (driver, args.url))

    logger.info(f'logging as {args.username}...')
    try_catch(login, (driver, args))

    logger.info('starting the recorder...')
    try_catch(start_recording_with_screen_recorder, (driver, ))

    logger.info('recorder is started, watching for freeze detection!')

    if args.debug:
        end_time = datetime.now() + timedelta(seconds=60)
    else:
        end_time = datetime.now() + timedelta(minutes=args.duration)

    old_screenshot = cv2.imdecode(np.frombuffer(
        driver.get_screenshot_as_png(), np.uint8), -1)
    next_failure_test = datetime.now() + FAILURE_TEST_INTERVAL
    while datetime.now() < end_time and is_need_recording():
        if datetime.now() >= next_failure_test:
            for retry_number in range(10):
                try:
                    cur_screenshot = cv2.imdecode(np.frombuffer(
                        driver.get_screenshot_as_png(), np.uint8), -1)
                    similarity = ssim(
                        old_screenshot, cur_screenshot, multichannel=True)
                    if similarity > 0.98:
                        logger.info(
                            'Screenshots are too similar, refresh!')
                        force_refresh(driver)
                        goto_class(driver)
                    old_screenshot = cur_screenshot
                    break
                except Exception as e:
                    logger.exception(e)
            next_failure_test = datetime.now() + FAILURE_TEST_INTERVAL

        time.sleep(max(0, min(
            10,
            (end_time - datetime.now()).total_seconds()
        )))

    logger.info('time is over. stopping the recorder...')
    try_catch(stop_recordering, args=(driver, ))

    logger.info("waiting for download to be complete...")
    if args.debug:
        time.sleep(2)
    else:
        time.sleep(60 + 3 * args.duration)

    logger.info("checking for download file existance...")
    for retry_number in range(100):
        try:
            if len(os.listdir(download_path)) == 0 or not os.listdir(
                    download_path)[0].endswith('.webm'):
                raise Exception('Downloaded file can not be found!')
                time.sleep(10 * (1 + retry_number))
            break
        except Exception as e:
            logger.exception(e)

    logger.info("closing all windows...")
    try_catch(close_all_windows, args=(driver, ))

    webm_file = os.path.join(
        download_path,
        os.listdir(download_path)[0]
    )
    new_webm_file = os.path.join(download_path, 'video.webm')
    os.rename(webm_file, new_webm_file)
    output_mp4 = os.path.join(download_path, 'video.mp4')

def main():
    parser = configure_parser()
    args = parser.parse_args()

    if args.url != '' and args.video != '':
        print('You cant define the -v argument for recording')
        exit()

    if args.url != '':
        record_video(args)
    else:
        new_webm_file = args.video
        output_mp4 = os.path.join(os.path.dirname(args.video), 'video.mp4')

    logger.info(f"now converting {new_webm_file} to mp4")
    ffmpeg_pipe = ffmpeg.input(new_webm_file)
    if args.encoding == "high":
        ffmpeg_pipe.output(
            output_mp4,
            **{'vcodec': 'libx264', 'acodec': 'aac', 'b:a': '128k', },
            crf='36',
            tune='stillimage',
            preset='veryfast',
            r='25',
            movflags='+faststart'
        ).run()
    elif args.encoding == "medium":
        ffmpeg_pipe.output(
            output_mp4,
            **{'vcodec': 'libx264', 'acodec': 'aac', 'b:a': '60k', },
            crf='36',
            tune='stillimage',
            preset='veryfast',
            s='852x480',
            r='20',
            movflags='+faststart'
        ).run()
    elif args.encoding == "low":
        ffmpeg_pipe.output(
            output_mp4,
            **{'vcodec': 'libx264', 'acodec': 'aac', 'b:a': '60k', },
            crf='36',
            tune='stillimage',
            preset='veryfast',
            s='640x360',
            r='15',
            movflags='+faststart'
        ).run()


if __name__ == "__main__":
    main()
