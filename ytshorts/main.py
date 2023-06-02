from YTShortDriver import YTShortDriver
from time import sleep
import json
from argparse import ArgumentParser
from time import sleep
import util
import pandas as pd
from util import classify
import os

PARAMETERS = dict(
    training_phase_n=10,
    training_phase_sleep=30,
    testing_phase_n=1000,
    intervention_phase_n=10,
    upper_bound=1000
)

STATE = dict(
    testing_phase_0_data=[],
    training_phase_1_data=[],
    training_phase_2_data=[],
    testing_phase_1_data=[],
    intervention_phase_1_data=[],
    testing_phase_2_data=[],
    intervention_phase_2_data=[],
    testing_phase_3_data=[]
)

def parse_args():
    args = ArgumentParser()
    args.add_argument('--q', required=True)
    args.add_argument('--i', help='Intervention Type', required=True)
    args.add_argument('--n', help='Account Name Type', required=True)
    args.add_argument('--outputDir', help='Output directory', required=True)
    return args.parse_args()

def training_phase_1(driver: YTShortDriver, query):
    with open('accounts.json') as f:
        json_file = json.load(f)
        accounts_list = json_file[query]
        for url in accounts_list:
            if url in STATE['training_phase_1_data']:
                continue
            sleep(2)
            driver.subscribe(url)
            STATE['training_phase_1_data'].append(url)

def training_phase_2(driver: YTShortDriver, query):

    driver.goto_shorts()
    start = len(STATE['training_phase_2_data'])
    count = len([i for i in STATE['training_phase_2_data'] if i.get('liked', False)])

    for iter in range(start, PARAMETERS['upper_bound']):

        # break if exit satisfied
        if count > PARAMETERS["training_phase_n"]:
            break

        # get current short
        short = driver.get_current_short()

        if classify(query, f"{short.metadata['title']} {short.metadata['description']}"):
            count += 1
            short.metadata['liked'] = True
            # click on like and watch for longer
            driver.positive_signal()
            sleep(PARAMETERS["training_phase_sleep"])

        # append to training data
        STATE['training_phase_2_data'].append(short.metadata)

        # swipe to next video
        driver.next_short()

def testing(driver: YTShortDriver, phase):
    # open shorts page
    driver.goto_shorts()

    # start testing
    start = len(STATE[f'testing_phase_{phase}_data'])

    for iter in range(start, PARAMETERS['testing_phase_n']):

        # grab current short
        short = driver.get_current_short()
        
        # append to training data
        STATE[f'testing_phase_{phase}_data'].append(short.metadata)
        
        # get next short
        driver.next_short()

def Not_Interested(driver: YTShortDriver, query, intervention, phase):
    intervention_data = STATE[f'intervention_phase_{phase}_data']
    driver.goto_shorts()
    
    count = len([i for i in intervention_data if i.get('Intervened', False)])
    start = len(intervention_data)

    # for 1000 videos
    for iter in range(start, PARAMETERS['upper_bound']):

        # break if success
        if count > PARAMETERS["intervention_phase_n"]:
            break
        
        # get current short
        short = driver.get_current_short()
        
        if classify(query, f"{short.metadata['title']} {short.metadata['description']}"):
            count += 1
            short.metadata['Intervened'] = True
            # click on like and watch for longer
            driver.negative_signal()

        intervention_data.append(short.metadata)

        # swipe to next video
        driver.next_short()

def Unfollow(driver: YTShortDriver, query, intervention, phase):
    driver.goto_shorts()
    sleep(2)
    driver.unfollow_all_accounts()

def login_controller(driver: YTShortDriver, name):
    credentials = pd.read_csv('credentials.csv', delimiter='\t')
    credential = credentials[credentials['email'].str.startswith(name)].iloc[0]
    try: driver.login(credential['email'], credential['password'])
    except: pass

def log(args, *message):
    print(*message)
    with open(f'{args.outputDir}/logs/{args.q}--{args.i}--{args.n}.logs', 'a') as f:
        for msg in message:
            f.write(str(msg))
        f.write('\n')

def save_state(args):
    with open(f'{args.outputDir}/state/{args.q}--{args.i}--{args.n}_state.json', 'w') as f:
        json.dump(STATE, f)

def load_state(args):
    global STATE
    if os.path.exists(f'{args.outputDir}/state/{args.q}--{args.i}--{args.n}_state.json'):
        with open(f'{args.outputDir}/state/{args.q}--{args.i}--{args.n}_state.json') as f:
            saved_state = json.load(f)
            for key, value in saved_state.items():
                STATE[key] = value

def main(args, driver: YTShortDriver):
    
    util.makedirs(args.outputDir)

    # pre login check
    driver.goto_homepage()
        
    # login
    login_controller(driver, args.n)
    
    ## take screenshot for login verification
    driver.save_screenshot(f'{args.outputDir}/screenshots/{args.q}--{args.i}--{args.n}__login.png')

    # one time goto shorts to clear out any prompts
    driver.goto_shorts()
    
    # testing phase 0
    log(args, "Testing Phase 0...", util.timestamp())
    testing(driver, 0)
    save_state(args)
    
    # training phase 1
    log(args, "Training Phase 1...", util.timestamp())
    training_phase_1(driver, args.q)
    save_state(args)

    # training phase 2
    log(args, "Training Phase 2...", util.timestamp())
    training_phase_2(driver, args.q)
    save_state(args)

    # testing phase 1
    log(args, "Testing Phase 1...", util.timestamp())
    testing(driver, 1)
    save_state(args)
    
    # intervention phase 1
    if args.i == "Not_Interested":
        log(args, "Not Interested First Intervention...", util.timestamp())
        Not_Interested(driver, args.q, args.i, 1)
        
    elif args.i == "Unfollow":
        log(args, "Unfollow First Intervention...", util.timestamp())
        Unfollow(driver, args.q, args.i, 1)
        
    save_state(args)

    # testing phase 2
    log(args, "Testing Phase 2... ", util.timestamp())
    testing(driver, 2)
    save_state(args)

    # intervention phase 2
    if args.i == "Not_Interested":
        log(args, "Not Interested First Intervention, Doing Unfollow now...", util.timestamp())
        Unfollow(driver, args.q, args.i, 2)
        
    elif args.i == "Unfollow":
        log(args, "Unfollow First Intervention, Doing Not Interested now...", util.timestamp())
        Not_Interested(driver, args.q, args.i, 2)
        
    save_state(args)

    # testing phase 3
    log(args, "Testing Phase 3...", util.timestamp())
    testing(driver, 3)
    save_state(args)

    # clean up
    log(args, "Finished!", util.timestamp())
    save_state(args)
    driver.close()

if __name__ == '__main__':
    args = parse_args()
    load_state(args)
    driver = YTShortDriver(profile_dir=os.path.join(args.outputDir, 'profiles', args.n), use_virtual_display=True)
    try:
        main(args, driver)
        with open(os.path.join(args.outputDir, 'completed_runs.txt'), 'a') as f:
            f.write(args.n + '\n')
    except Exception as e:
        log(args, e)
        driver.save_screenshot(f'{args.outputDir}/screenshots/{args.q}--{args.i}--{args.n}_error.png')
    finally:
        save_state(args)