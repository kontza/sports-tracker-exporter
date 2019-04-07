#!/usr/bin/env python3
import argparse
import datetime
import getpass
import json
import logging
import os
import os.path
import sys

try:
    import requests
except:
    print('''You need to pip install requests:

    $ pip3 install --user --upgrade requests''')
    sys.exit(1)

logging.basicConfig(format='%(asctime)-15s %(levelname)7s %(message)s', level=logging.INFO)
logger = logging.getLogger(os.path.splitext(os.path.split(__file__)[-1])[0])
workout_list = 'workouts.stdl'


class VerboseAction(argparse.Action):
    def __init__(self, nargs=0, **kw):
        if nargs != 0:
            raise ValueError('nargs for VerboseAction must be 0; it is just a flag.')
        super().__init__(nargs=nargs, **kw)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True)
        logger.setLevel(logging.DEBUG)
        logger.debug('Logging verbosely.')


def download_workout(args, session, workout_key):
    'https://sports-tracker.com/apiserver/v1/workout/exportGpx/55db4fc1e4b094b778d42ed5?token=e78qo9jpe61f87p9d2baa1eq82qv60ui'
    pass


def get_list(args, session, output_filepath):
    url = 'https://sports-tracker.com/apiserver/v1/workouts'
    logger.info('Loading workouts, this might take a while...')
    req = session.get(url, params={'limited': 'true', 'limit': 1000000})
    if req.status_code >= 200 and req.status_code < 300:
        logger.info('Workouts ({}) loaded...'.format(len(req.json()['payload'])))
        with open(output_filepath, 'w') as output_file:
            json.dump(req.json(), output_file, ensure_ascii=False, indent=2)
    else:
        logger.error('Failed to get the workout list: {} {}'.format(req.status_code, req.text))


def run(args):
    output_filepath = os.path.join(args.directory, workout_list)
    if os.path.exists(output_filepath):
        logger.info("Workouts list ({}) already exists, using it instead of downloading a new one.".format(output_filepath))
    else:
        logger.info('Logging in to Sports Tracker.')
        url = 'https://sports-tracker.com/apiserver/v1/login'
        password = getpass.getpass('Enter your Sports Tracker password: ')
        session = requests.Session()
        req = session.post(url, params={'source': 'javascript'}, data={'l': args.user, 'p': password})
        if req.status_code >= 200 and req.status_code < 300:
            logger.info('Welcome {}.'.format(req.json()['realName']))
            logger.debug("Response: {}".format(req.json()))
            session.headers.update({'sttauthorization': req.json()['userKey']})
            get_list(args, session, output_filepath)
        else:
            logger.error('Login failed: {} {}'.format(req.status_code, req.text))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download excercises from Sports Tracker.')
    parser.add_argument('-v', '--verbose', help='increase output verbosity', action=VerboseAction)
    parser.add_argument('-d', '--directory', default=os.getcwd(), help='the directory where to store exported files')
    parser.add_argument('user', help='the user to log in as')
    args = parser.parse_args()
    if not os.path.exists(args.directory):
        logger.error("Output directory '{}' does not exist, cannot continue".format(args.directory))
        exit()
    run(args)
    logger.info('All done, TTFN.')
