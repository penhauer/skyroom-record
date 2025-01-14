import pyautogui

from datetime import datetime
from flask import Flask, send_file, render_template, request
from flask import jsonify, abort
import crontab
import threading
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
pyautogui.FAILSAFE = False


@app.route('/')
def hello_world():
    return render_template('debug.html')


@app.route('/screen')
def screen():
    screenshot_path = '../downloads/my_screenshot.png'
    pyautogui.screenshot(screenshot_path)
    return send_file(screenshot_path, last_modified=datetime.now())


@app.route('/click', methods=['POST'])
def click_on_page():
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))
    pyautogui.moveTo(x, y)
    pyautogui.click()
    return 'ok'


@app.route('/get_pixel')
def get_pixel():
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))
    color = pyautogui.pixel(x, y)
    return f'{x}, {y}:  {color.red}, {color.green}, {color.blue}'


@app.route('/stop-recording', methods=['POST'])
def stop_recording():
    with open('./force-stop-recording', 'w') as f:
        f.write('1')
    return 'ok'


def run_crons():
    tab = crontab.CronTab(tabfile='cron-tabs.tab')
    logging.info("starting cron scheduler")
    for result in tab.run_scheduler():
        logging.info("starting task ============================================")
        logging.info(result)


threading.Thread(target=run_crons).start()