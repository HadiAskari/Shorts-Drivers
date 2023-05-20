from ReelsDriver import ReelsDriver
from time import sleep
import json
from argparse import ArgumentParser
from time import sleep
import util
import pandas as pd
from util import classify

PARAMETERS = dict(
    training_phase_n=10,
    training_phase_sleep=30,
    testing_phase_n=1000,
    intervention_phase_n=10,
    upper_bound=1000
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
            sleep(2)
            driver.subscribe(url)

def training_phase_2(driver: ReelsDriver, query):
    #need to change

    driver.goto_shorts()
    count = 0
    # start training
    training_phase_2_data = []

    for iter in range(PARAMETERS['upper_bound']):

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
        training_phase_2_data.append(short.metadata)

        # swipe to next video
        driver.next_short()
    
    return training_phase_2_data


def testing(driver: ReelsDriver):

    # open shorts page
    driver.goto_shorts()

    # start testing
    testing_phase1_data = []
    count = 0
    for iter in range(PARAMETERS["testing_phase_n"]):

        # grab current short
        short = driver.get_current_short()

        # append to training data
        testing_phase1_data.append(short.metadata)
        count += 1
        
        # get next short
        driver.next_short()

    return testing_phase1_data

def Not_Interested(driver: ReelsDriver,query, intervention):
    #need to change

    driver.goto_shorts()

    sleep(2)
    
    intervention_data = []
    count = 0

    # for 1000 videos
    for iter in range(PARAMETERS['upper_bound']):

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

        intervention_data.append(short.metadata)

        # swipe to next video
        driver.next_short()

    return intervention_data

def Unfollow(driver: ReelsDriver,query, intervention):
    #need to change
    driver.goto_shorts()

    sleep(2)
    
    intervention_data = []
  
    driver.unfollow_all_accounts()

    return intervention_data

def Unfollow_Not_Interested(driver: ReelsDriver,query, intervention):

    driver.unfollow_all_accounts()
    sleep(2)

    driver.goto_shorts()
    sleep(2)

    intervention_data = []
    count = 0

    # for 1000 videos
    for iter in range(PARAMETERS['upper_bound']):

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

        intervention_data.append(short.metadata)

        # swipe to next video
        driver.next_short()

    return intervention_data

def Not_Interested_Unfollow(driver: ReelsDriver,query, intervention):
    #need to change

    driver.goto_shorts()


    sleep(2)
    
    intervention_data = []
    count = 0

    # for 1000 videos
    for iter in range(PARAMETERS['upper_bound']):

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

        intervention_data.append(short.metadata)

        # swipe to next video
        driver.next_short()


    driver.unfollow_all_accounts()


    return intervention_data

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

def main(args, driver):
    util.makedirs(args.outputDir)

    # clear out log files
    with open(f'{args.outputDir}/logs/{args.q}--{args.i}--{args.n}.logs', 'w') as f:
        pass

    login_controller(driver, args.n)
    
    driver.goto_homepage()

    driver.save_screenshot(f'{args.outputDir}/screenshots/{args.q}--{args.i}--{args.n}.png')

    log(args, "Training Phase 1...", util.timestamp())
    training_phase_1(driver, args.q)

    log(args, "Training Phase 2...", util.timestamp())
    training_phase_2_data = training_phase_2(driver, args.q)
    
    log(args, "Testing Phase 1...", util.timestamp())
    testing_phase_1_data = testing(driver)

    log(args, "Saving...", util.timestamp())
    pd.DataFrame(training_phase_2_data).to_csv(f'{args.outputDir}/training_phase_2/{args.q}--{args.i}--{args.n}_tr_p2.csv', index=False)
    pd.DataFrame(testing_phase_1_data).to_csv(f'{args.outputDir}/testing_phase_1/{args.q}--{args.i}--{args.n}_te_p1.csv', index=False)


    if args.i == "Not_Interested":
    
        log(args, "Not Interested Only Intervention...", util.timestamp())
        intervention_data = Not_Interested(driver, args.q, args.i)
        pd.DataFrame(intervention_data).to_csv(f'{args.outputDir}/intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)
    
    elif args.i == "Unfollow":
        log(args, "Unfollow Only Intervention...", util.timestamp())
        intervention_data = Unfollow(driver, args.q, args.i)
        pd.DataFrame(intervention_data).to_csv(f'{args.outputDir}/intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)

    elif args.i == "Unfollow_Not_Interested":
        log(args, "Unfollow then Not Interested Intervention...", util.timestamp())
        intervention_data = Unfollow_Not_Interested(driver, args.q, args.i)
        pd.DataFrame(intervention_data).to_csv(f'{args.outputDir}/intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)

    elif args.i == "Not_Interested_Unfollow":
        log(args, "Not Interested then Unfollow Intervention...", util.timestamp())
        intervention_data = Not_Interested_Unfollow(driver, args.q, args.i)
        pd.DataFrame(intervention_data).to_csv(f'{args.outputDir}/intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)

    elif args.i == "Control":
        log(args, "Control Intervention")
        intervention_data = Control()
        pd.DataFrame(intervention_data).to_csv(f'{args.outputDir}/intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)

    
    log(args, "Testing Phase 2... ", util.timestamp())
    testing_phase_2_data = testing(driver)

    log(args, "Saving...")
    
    pd.DataFrame(testing_phase_2_data).to_csv(f'{args.outputDir}/testing_phase_2/{args.q}--{args.i}--{args.n}_te_p2.csv', index=False)

    driver.close()

if __name__ == '__main__':
    args = parse_args()
    driver = ReelsDriver(use_virtual_display=True)
    try:
        main(args, driver)
    except Exception as e:
        log(args, e)
        driver.save_screenshot(f'{args.outputDir}/screenshots/{args.q}--{args.i}--{args.n}_error.png')