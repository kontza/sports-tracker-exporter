#!/usr/bin/env python3
import argparse
import datetime
import dotenv
import getpass
import io
import json
import logging
import os
import os.path
import requests

logging.basicConfig(format='%(asctime)-15s %(levelname)7s %(message)s', level=logging.INFO)
logger = logging.getLogger(os.path.splitext(os.path.split(__file__)[-1])[0])
workout_list = 'workouts.stdl'
activities = [
    'Walking',
    'Running',
    'Cycling',
    'Nordic_skiing',
    'Other_1',
    'Other_2',
    'Other_3',
    'Other_4',
    'Other_5',
    'Other_6',
    'Mountain_biking',
    'Hiking',
    'Roller_skating',
    'Downhill_skiing',
    'Paddling',
    'Rowing',
    'Golf',
    'Indoor',
    'Parkour',
    'Ball_games',
    'Outdoor_gym',
    'Swimming',
    'Trail_running',
    'Gym',
    'Nordic_walking',
    'Horseback_riding',
    'Motorsports',
    'Skateboarding',
    'Water_sports',
    'Climbing',
    'Snowboarding',
    'Ski_touring',
    'Fitness_class',
    'Soccer',
    'Tennis',
    'Basketball',
    'Badminton',
    'Baseball',
    'Volleyball',
    'American_football',
    'Table_tennis',
    'Racquet_ball',
    'Squash',
    'Floorball',
    'Handball',
    'Softball',
    'Bowling',
    'Cricket',
    'Rugby'
]


class VerboseAction(argparse.Action):
    def __init__(self, nargs=0, **kw):
        if nargs != 0:
            raise ValueError('nargs for VerboseAction must be 0; it is just a flag.')
        super().__init__(nargs=nargs, **kw)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True)
        logger.setLevel(logging.DEBUG)
        logger.debug('Logging verbosely.')


def download_workout(args, session, output_dir, timestamp, workout_key, activity_id):
    url = 'https://sports-tracker.com/apiserver/v1/workout/exportFit/{}'.format(workout_key)
    token = None
    try:
        token = session.headers['sttauthorization']
    except KeyError:
        logger.info('sttauthorization not found in session, not logged in.')
        if login(args, session):
            token = session.headers['sttauthorization']
        else:
            return
    logger.info('Downloading workout from {}...'.format(timestamp))
    req = session.get(url, params={'token': token})
    activity_name = ''
    try:
        activity_name = activities[activity_id]
    except:
        logger.error('Activity {} not in the predefined list.'.format(activity_id))
        activity_name = workout_key
    output_filepath = os.path.join(output_dir, '{}-{}.fit'.format(
        timestamp.isoformat().replace('T', '_').replace(':', '_'), activity_name))
    with open(output_filepath, 'wb') as output_file:
        output_file.write(io.BytesIO(req.content).read())
        logger.info("Workout saved to '{}'.".format(output_filepath))


def get_list(args, session, output_filepath):
    url = 'https://sports-tracker.com/apiserver/v1/workouts'
    logger.info('Loading workouts, this might take a while...')
    req = session.get(url, params={'limited': 'true', 'limit': 1000000})
    if req.status_code >= 200 and req.status_code < 300:
        logger.info('Workouts ({}) loaded...'.format(len(req.json()['payload'])))
        with open(output_filepath, 'w') as output_file:
            json.dump(req.json()['payload'], output_file, ensure_ascii=False)
    else:
        logger.error('Failed to get the workout list: {} {}'.format(req.status_code, req.text))


def process_workout_list(args, session, workout_list):
    with open(workout_list, 'r') as workouts_file:
        workouts = json.load(workouts_file)
        counter = 1
        for workout in workouts:
            timestamp = datetime.datetime.fromtimestamp(int(workout['startTime'] / 1000))
            logger.info('Workout {}/{} from {}: {}.'.format(counter, len(workouts), timestamp, workout['workoutKey']))
            download_workout(args,
                             session,
                             os.path.split(workout_list)[0],
                             timestamp,
                             workout['workoutKey'],
                             workout['activityId'])
            counter += 1


def login(args, session):
    logger.info('Logging in to Sports Tracker.')
    url = 'https://sports-tracker.com/apiserver/v1/login'
    if not args.password:
        args.password = getpass.getpass('Enter your Sports Tracker password: ')
    req = session.post(url, params={'source': 'javascript'}, data={'l': args.user, 'p': args.password})
    ret_val = False
    if req.status_code >= 200 and req.status_code < 300:
        logger.info('Welcome {}.'.format(req.json()['realName']))
        logger.debug('Response: {}'.format(req.json()))
        session.headers.update({'sttauthorization': req.json()['userKey']})
        ret_val = True
    else:
        logger.error('Login failed: {} {}'.format(req.status_code, req.text))
    return ret_val


def run(args):
    workouts_filepath = os.path.join(args.directory, workout_list)
    session = requests.Session()
    if os.path.exists(workouts_filepath):
        logger.info('Workouts list ({}) already exists, using it instead of downloading a new one.'.format(workouts_filepath))
    else:
        if login(args, session):
            get_list(args, session, workouts_filepath)
    process_workout_list(args, session, workouts_filepath)


if __name__ == '__main__':
    dotenv.load_dotenv()
    parser = argparse.ArgumentParser(description='Download excercises from Sports Tracker.')
    parser.add_argument('-v', '--verbose', help='increase output verbosity', action=VerboseAction)
    parser.add_argument('-d', '--directory', default=os.getcwd(), help='the directory where to store exported files')
    parser.add_argument('-u', '--user', help='the user to log in as', default=os.getenv('SPORTS_TRACKER_USERNAME'))
    args = parser.parse_args()
    if not os.path.exists(args.directory):
        logger.error("Output directory '{}' does not exist, cannot continue".format(args.directory))
        exit()
    args.password = os.getenv('SPORTS_TRACKER_PASSWORD')
    run(args)
    logger.info('All done, TTFN.')
