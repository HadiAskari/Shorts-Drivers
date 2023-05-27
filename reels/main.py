from ReelsDriver import ReelsDriver
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
    training_phase_1_data=[],
    training_phase_2_data=[],
    testing_phase_1_data=[],
    intervention_data=[],
    testing_phase_2_data=[]
)

def parse_args():
    args = ArgumentParser()
    args.add_argument('--q', required=True)
    args.add_argument('--i', help='Intervention Type', required=True)
    args.add_argument('--n', help='Account Name Type', required=True)
    args.add_argument('--outputDir', help='Output directory', required=True)
    return args.parse_args()

def training_phase_1(driver: ReelsDriver, query):
    with open('accounts.json') as f:
        json_file = json.load(f)
        accounts_list = json_file[query]
        for url in accounts_list:
            if url in STATE['training_phase_1_data']:
                continue
            sleep(2)
            driver.subscribe(url)
            STATE['training_phase_1_data'].append(url)

def training_phase_2(driver: ReelsDriver, query):
    driver.goto_shorts()
    start = len(STATE['training_phase_2_data'])
    count = len([i for i in STATE['training_phase_2_data'] if i.get('liked', False)])

    for iter in range(start, PARAMETERS['upper_bound']):

        # break if exit satisfied
        if count > PARAMETERS["training_phase_n"]:
            break

        # get current short
        short = driver.get_current_short()

        if classify(query, short.metadata['description']):
            count += 1
            short.metadata['liked'] = True
            # click on like and watch for longer
            driver.positive_signal()
            sleep(PARAMETERS["training_phase_sleep"])

        # append to training data
        STATE['training_phase_2_data'].append(short.metadata)

        # swipe to next video
        driver.next_short()

def testing(driver: ReelsDriver, phase):
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

def Not_Interested(driver: ReelsDriver, query, intervention):
    driver.goto_shorts()
    
    count = len([i for i in STATE['intervention_data'] if i.get('Intervened', False)])
    start = len(STATE['intervention_data'])

    # for 1000 videos
    for iter in range(start, PARAMETERS['upper_bound']):

        # break if success
        if count > PARAMETERS["intervention_phase_n"]:
            break
        
        # get current short
        short = driver.get_current_short()
        
        if classify(query, short.metadata['description']):
            count += 1
            short.metadata['Intervened'] = True
            # click on like and watch for longer
            driver.negative_signal()

        STATE['intervention_data'].append(short.metadata)

        # swipe to next video
        driver.next_short()

def Unfollow(driver: ReelsDriver, query, intervention):
    driver.goto_shorts()
    sleep(2)
    driver.unfollow_all_accounts()

def Unfollow_Not_Interested(driver: ReelsDriver, query, intervention):

    driver.unfollow_all_accounts()
    sleep(2)

    driver.goto_shorts()
    sleep(2)
    
    count = len([i for i in STATE['intervention_data'] if i.get('Intervened', False)])
    start = len(STATE['intervention_data'])

    for iter in range(start, PARAMETERS['upper_bound']):

        # break if success
        if count > PARAMETERS["intervention_phase_n"]:
            break
        
        # get current short
        short = driver.get_current_short()
        
        if classify(query, short.metadata['description']):
            count += 1
            short.metadata['Intervened'] = True
            # click on like and watch for longer
            driver.negative_signal()

        STATE['intervention_data'].append(short.metadata)

        # swipe to next video
        driver.next_short()

def Not_Interested_Unfollow(driver: ReelsDriver,query, intervention):
    
    driver.goto_shorts()
    sleep(2)
    
    count = len([i for i in STATE['intervention_data'] if i.get('Intervened', False)])
    start = len(STATE['intervention_data'])

    for iter in range(start, PARAMETERS['upper_bound']):

        # break if success
        if count > PARAMETERS["intervention_phase_n"]:
            break
        
        # get current short
        short = driver.get_current_short()

        if classify(query, short.metadata['description']):
            count += 1
            short.metadata['Intervened'] = True
            # click on like and watch for longer
            driver.negative_signal()

        STATE['intervention_data'].append(short.metadata)

        # swipe to next video
        driver.next_short()

    driver.unfollow_all_accounts()

def Control():
    pass

def login_controller(driver: ReelsDriver, name):
    with open('credentials.json') as f:
        json_file = json.load(f)
        accounts_list = json_file[name]
    driver.login(accounts_list[0], accounts_list[1])

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
            STATE = json.load(f)

def main(args, driver: ReelsDriver):
    
    util.makedirs(args.outputDir)
    
    # login
    login_controller(driver, args.n)
    
    ## take screenshot for login verification
    driver.save_screenshot(f'{args.outputDir}/screenshots/{args.q}--{args.i}--{args.n}__login.png')

    # training phase 1
    log(args, "Training Phase 1...", util.timestamp())
    training_phase_1(driver, args.q)
    save_state(args)

    ## take profile screenshot for verification
    driver.goto_profile()
    driver.save_screenshot(f'{args.outputDir}/screenshots/{args.q}--{args.i}--{args.n}__profile.png')

    # training phase 2
    log(args, "Training Phase 2...", util.timestamp())
    training_phase_2(driver, args.q)
    save_state(args)

    # testing phase 1
    log(args, "Testing Phase 1...", util.timestamp())
    testing(driver, 1)
    save_state(args)
    
    # intervention phase
    if args.i == "Not_Interested":
        log(args, "Not Interested Only Intervention...", util.timestamp())
        Not_Interested(driver, args.q, args.i)
        
    elif args.i == "Unfollow":
        log(args, "Unfollow Only Intervention...", util.timestamp())
        Unfollow(driver, args.q, args.i)
        
    elif args.i == "Unfollow_Not_Interested":
        log(args, "Unfollow then Not Interested Intervention...", util.timestamp())
        Unfollow_Not_Interested(driver, args.q, args.i)
        
    elif args.i == "Not_Interested_Unfollow":
        log(args, "Not Interested then Unfollow Intervention...", util.timestamp())
        Not_Interested_Unfollow(driver, args.q, args.i)
        
    elif args.i == "Control":
        log(args, "Control Intervention")
        Control()
        
    save_state(args)

    # testing phase 2
    log(args, "Testing Phase 2... ", util.timestamp())
    testing(driver, 2)
    save_state(args)

    driver.close()

if __name__ == '__main__':
    args = parse_args()
    load_state(args)
    driver = ReelsDriver(use_virtual_display=True)
    try:
        main(args, driver)
        with open(os.path.join(args.outputDir, 'completed_runs.txt'), 'a') as f:
            f.write(args.n + '\n')
    except Exception as e:
        log(args, e)
        driver.save_screenshot(f'{args.outputDir}/screenshots/{args.q}--{args.i}--{args.n}_error.png')
    finally:
        save_state(args)