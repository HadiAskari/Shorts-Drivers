from YTShortDriver import YTShortDriver
import os
from time import sleep
from shutil import rmtree
import json
from argparse import ArgumentParser
from random import randint
from time import sleep
import util
import pandas as pd
import re
from tqdm.auto import tqdm
from util import classify


PARAMETERS = dict(
    training_phase_n=10,
    training_phase_sleep=30,
    testing_phase_n=1000,
    intervention_phase_n=10
)

def parse_args():
    args = ArgumentParser()
    args.add_argument('--q', required=True)
    args.add_argument('--i', help='Intervention Type', required=True)
    #args.add_argument('--d', help='Device Index', required=False, type=int)
    args.add_argument('--n', help='Account Name Type', required=True)
    return args.parse_args()




#write code for training phase 1 as well

def training_phase_1(driver: YTShortDriver, query):
    with open('accounts.json') as f:
        json_file = json.load(f)
        accounts_list=json_file[query]
        for url in accounts_list:
            sleep(2)
            driver.subscribe(url)




def training_phase_2(driver: YTShortDriver, query):

    driver.goto_shorts()

    sleep(2)

    count = 0
    # start training
    training_phase_2_data = []

    for iter in tqdm(range(1000)):

        # break if exit satisfied
        if count > PARAMETERS["training_phase_n"]:
            break

        # get current short
        short = driver.get_current_short()

        #print(short.metadata['description'])

        if classify(query, short.metadata['description']):
            count += 1
            short.metadata['liked'] = True
            # click on like and watch for longer
            sleep(PARAMETERS["training_phase_sleep"])
            driver.positive_signal()

    
        # append to training data
        training_phase_2_data.append(short.metadata)

        # swipe to next video
        driver.next_short()
    
    return training_phase_2_data


def testing(driver: YTShortDriver):
   
        # open shorts page
    driver.goto_shorts()

    sleep(2)

    # start testing
    testing_phase1_data = []
    count = 0
    for iter in tqdm(range(PARAMETERS["testing_phase_n"])):

        # grab current short
        short = driver.get_current_short()

        #print(short.metadata['description'])

        # append to training data
        testing_phase1_data.append(short.metadata)
        count += 1
        
        # get next short
        driver.next_short()

    return testing_phase1_data

  


def Not_Interested(driver: YTShortDriver,query, intervention):
    #need to change
    driver.goto_shorts()

    sleep(2)
    
    intervention_data = []
    count = 0

    # for 1000 videos
    for iter in tqdm(range(1000)):

        # break if success
        if count > PARAMETERS["intervention_phase_n"]:
            print('breaking',count)
            break
        
        # get current short
        short = driver.get_current_short()

        
        if classify(query, short.metadata['description']):
            count += 1
            short.metadata['Intervened'] = True
            # click on like and watch for longer
            driver.negative_signal()

        training_phase_2_data.append(short.metadata)

        # swipe to next video
        driver.next_short()

    return intervention_data

def Unfollow(driver: YTShortDriver,query, intervention):
    #need to change
    driver.goto_shorts()

    sleep(2)
    
    intervention_data = []
  
    driver.unfollow_all_accounts()

    return intervention_data

def Unfollow_Not_Interested(driver: YTShortDriver,query, intervention):
    #need to change


    sleep(2)
 
    intervention_data = []

    driver.unfollow_all_accounts()


    #need to change
    driver.goto_shorts()


    sleep(2)
    
    intervention_data = []
    count = 0

    # for 1000 videos
    for iter in tqdm(range(1000)):

        # break if success
        if count > PARAMETERS["intervention_phase_n"]:
            print('breaking',count)
            break
        
        # get current short
        short = driver.get_current_short()

        
        if classify(query, short.metadata['description']):
            count += 1
            short.metadata['Intervened'] = True
            # click on like and watch for longer
            driver.negative_signal()

        training_phase_2_data.append(short.metadata)

        # swipe to next video
        driver.next_short()


            

    return intervention_data
        

def Not_Interested_Unfollow(driver: YTShortDriver,query, intervention):
    #need to change

    driver.goto_shorts()


    sleep(2)
    
    intervention_data = []
    count = 0

    # for 1000 videos
    for iter in tqdm(range(1000)):

        # break if success
        if count > PARAMETERS["intervention_phase_n"]:
            print('breaking',count)
            break
        
        # get current short
        short = driver.get_current_short()

        
        if classify(query, short.metadata['description']):
            count += 1
            short.metadata['Intervened'] = True
            # click on like and watch for longer
            driver.negative_signal()

        training_phase_2_data.append(short.metadata)

        # swipe to next video
        driver.next_short()


    driver.unfollow_all_accounts()



    return intervention_data

def Control():
    pass
        

    
profile = "hadiaskari23"

if __name__ == '__main__':
        args = parse_args()
        driver = YTShortDriver(use_virtual_display=False, profile_dir='profiles/%s' % profile)
        
        # print("Launching emulator...")
        # device = emulate_new_device(credentials.name)
        #device = get_connected_devices()[args.d]


    # try:
        
        #configure_keyboard(device)

        driver.goto_homepage()

        # wait for user setup
        input("Start?")

        
        print("Training Phase 1...", util.timestamp())
        training_phase_1(driver, args.q)

        print("Training Phase 2...", util.timestamp())
        training_phase_2_data = training_phase_2(driver, args.q)
        
        print("Testing Phase 1...", util.timestamp())
        testing_phase_1_data = testing(driver)

        print("Saving...", util.timestamp())
        pd.DataFrame(training_phase_2_data).to_csv(f'training_phase_2/{args.q}--{args.i}--{args.n}_tr_p2.csv', index=False)
        pd.DataFrame(testing_phase_1_data).to_csv(f'testing_phase_1/{args.q}--{args.i}--{args.n}_te_p1.csv', index=False)


        if args.i == "Not_Interested":
       
            print("Not Interested Only Intervention...", util.timestamp())
            intervention_data = Not_Interested(driver,args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)
        
        elif args.i == "Unfollow":
            print("Unfollow Only Intervention...", util.timestamp())
            intervention_data = Unfollow(driver,args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)

        elif args.i == "Unfollow_Not_Interested":
            print("Unfollow then Not Interested Intervention...", util.timestamp())
            intervention_data = Unfollow_Not_Interested(driver,args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)

        elif args.i == "Not_Interested_Unfollow":
            print("Not Interested then Unfollow Intervention...", util.timestamp())
            intervention_data = Not_Interested_Unfollow(driver,args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)

        elif args.i == "Control":
            print("Control Intervention")
            intervention_data = Control(driver,args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)

        print("Testing Phase 2... ", util.timestamp())
        testing_phase_2_data = testing(driver)

        print("Saving...")
    #     pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}_{credentials.name}.csv', index=False)
    #     pd.DataFrame(testing_phase_2_data).to_csv(f'testing_phase_2/{args.q}_{credentials.name}.csv', index=False)
        
        pd.DataFrame(testing_phase_2_data).to_csv(f'testing_phase_2/{args.q}--{args.i}--{args.n}_te_p2.csv', index=False)

        driver.close()