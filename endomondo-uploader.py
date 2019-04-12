#!/usr/bin/env python3
import argparse
import atexit
import glob
import logging
import os
import os.path
import shutil
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

chrome_driver = webdriver.Chrome()
logging.basicConfig(format='%(asctime)-15s %(levelname)7s %(message)s', level=logging.INFO)
logger = logging.getLogger(os.path.splitext(os.path.split(__file__)[-1])[0])


class VerboseAction(argparse.Action):
    def __init__(self, nargs=0, **kw):
        if nargs != 0:
            raise ValueError('nargs for VerboseAction must be 0; it is just a flag.')
        super().__init__(nargs=nargs, **kw)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True)
        logger.setLevel(logging.DEBUG)
        logger.debug('Logging verbosely.')


@atexit.register
def driver_quit():
    print('Closing the Chromedriver.')
    chrome_driver.quit()


def login():
    try:
        chrome_driver.get("https://www.endomondo.com/login")
        wait = WebDriverWait(chrome_driver, 10)
        wait.until(lambda d: d.find_element_by_name("email"))
        inputElement = chrome_driver.find_element_by_name("email")
        inputElement.send_keys(os.getenv('ENDOMONDO_USERNAME'))
        inputElement = chrome_driver.find_element_by_name("password")
        inputElement.send_keys(os.getenv('ENDOMONDO_PASSWORD'))
        inputElement.submit()
    except TimeoutException as e:
        print('Login failed: {}'.format(e))
        return False
    return True


def logout():
    avatar_element = chrome_driver.find_element_by_class_name("header-member-profile")
    hover = ActionChains(chrome_driver).move_to_element(avatar_element)
    hover.perform()
    try:
        wait = WebDriverWait(chrome_driver, 10)
        log_out = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@ng-click="logout()"]')))
        log_out.click()
    except TimeoutException:
        print('Timed out while waiting for logout-button to be clickable.')


def upload(fit_file):
    chrome_driver.get('https://www.endomondo.com/workouts/create')
    try:
        # Handle import type selection.
        wait = WebDriverWait(chrome_driver, 10)
        # wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@id="ida"]'))).click()
        fileimport_div = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="fileImport"]')))
        step_up = fileimport_div.find_element_by_xpath('..')
        fileimport_btn = step_up.find_element_by_xpath('..')
        fileimport_btn.click()
        # Handle the file selection iframe.
        WebDriverWait(chrome_driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CLASS_NAME, "iframed")))
        upload_file = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@name="uploadFile"]')))
        full_path = os.path.abspath(fit_file)
        upload_file.send_keys(full_path)
        chrome_driver.find_element_by_xpath('//a[@name="uploadSumbit"]').click()
        wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@name="reviewSumbit"]'))).click()
        wait.until(EC.url_matches("/workouts/latest$"))
        # Transfer done, rename file.
        shutil.move(full_path, '{}.done'.format(full_path))
    except TimeoutException:
        print('Timed out while waiting to click file import buttons.')
        exit()


def run(args):
    if not login():
        exit()

    try:
        wait = WebDriverWait(chrome_driver, 10)
        wait.until(lambda d: d.current_url == "https://www.endomondo.com/home")
    except TimeoutException:
        print('Timed out on entering the landing page.')
        exit()

    # Close the premium ad.
    try:
        wait = WebDriverWait(chrome_driver, 10)
        dismiss = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'MonthTrialPopup-close')))
        dismiss.click()
    except TimeoutException:
        print('No popup this time, good.')

    # Loop over fit-files.
    for fit in sorted(glob.glob(os.path.join(args.directory,'*.fit'))):
        upload(fit)
        time.sleep(5)

    # Log out.
    logout()


if __name__ == '__main__':
    load_dotenv()
    parser = argparse.ArgumentParser(description='Upload excercises to Endomondo.')
    parser.add_argument('-v', '--verbose', help='increase output verbosity', action=VerboseAction)
    parser.add_argument('-d', '--directory', default=os.getcwd(), help='the directory where to load fit-files from')
    parser.add_argument('-u', '--user', help='the user to log in as', default=os.getenv('ENDOMONDO_USERNAME'))
    args = parser.parse_args()
    if not os.path.exists(args.directory):
        logger.error("Output directory '{}' does not exist, cannot continue".format(args.directory))
        exit()
    args.password = os.getenv('ENDOMONDO_PASSWORD')
    run(args)
    logger.info('All done, TTFN.')
