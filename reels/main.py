from ReelsDriver import ReelsDriver
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
    args.add_argument('--n', help='Account Name Type', required=True)
    return args.parse_args()

def training_phase_1(device,query):
    pass

def training_phase_2(driver: ReelsDriver, query):
    #need to change


    count = 0
    # start training
    training_phase_2_data = []

    for iter in tqdm(range(1000)):

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
    for iter in tqdm(range(PARAMETERS["testing_phase_n"])):

        # grab current short
        short = driver.get_current_short()

        # append to training data
        testing_phase1_data.append(short.metadata)
        count += 1
        
        # get next short
        driver.next_short()

    return testing_phase1_data


def Not_Interested(device,query, intervention):
    #need to change



    if intervention == "Not_Interested":
        pass 
    
    intervention_data = []
    count = 0

    # for 1000 videos
    for iter in tqdm(range(1000)):

        # restart every 50 videos to refresh app state
        if iter % 20 == 0:
            restart_app(device)

        # break if success
        if count > PARAMETERS["intervention_phase_n"]:
            print('breaking',count)
            break
    
        # check for any flow disruptions first
        #util.check_disruptions(device)
        
        # watch short for a certain time
        sleep(1)

        

        xml = device.get_xml()
        text_elems = device.find_elements({'content-desc': re.compile('.+')}, xml)
        text_elems += device.find_elements({'text': re.compile('.+')}, xml)

        # build row
        row = {}
        for column_id, elem in enumerate(text_elems):
            key = elem['resource-id']
            if key.strip() == '':
                key = 'col_%s' % column_id
            text = elem['content-desc']
            if text.strip() == '':
                text = elem['text']
            if text == '':
                continue
            row[key] = text
            
            if elem['resource-id'] == 'com.google.android.youtube:id/reel_main_title' and classify(query, text):
                count += 1
                row['Intervened'] = True
                row['Intervention'] = intervention
                print(text)

                #longtap
                device.longtap()
                sleep(1)

                # click on Not intereseted
                try: util.tap_on(device, {'text': "Don't recommend this channel"})
                except: util.swipe_up(device)

        intervention_data.append(row)

        # swipe to next video only if did not intervene here
        if not row.get('Intervened'):
            util.swipe_up(device)
        

    return intervention_data

def Unfollow(device,query, intervention):
    #need to change



    if intervention=="Unfollow":
        pass 
    
    restart_app(device)

    intervention_data = []

    sleep(10)

    # press on hide to hide content
    try: util.tap_on(device, attrs={'content-desc': 'Subscriptions'})
    except: pass

    util.tap_on(device, {'resource-id':"com.google.android.youtube:id/channels_button"})

    xml = device.get_xml()
    elems = device.find_elements({'class':"android.view.ViewGroup", "clickable":"true"}, xml)
    for n in range(1, len(elems), 2):
        # click bell icon
        util.tap_on_nth(device, {'class':"android.view.ViewGroup", "clickable":"true"}, n, xml)
        sleep(1)
        # click unsubscribe
        device.tap((300, 1500))
        sleep(1)

    return intervention_data

def Unfollow_Not_Interested(device,query, intervention):
    #need to change



    try:
        if intervention=="Unfollow_Not_Interested":
            pass 
            
        restart_app(device)

        intervention_data = []

        # press on hide to hide content
        try: util.tap_on(device, attrs={'content-desc': 'Subscriptions'})
        except: pass

        try: util.tap_on(device, {'resource-id':"com.google.android.youtube:id/channels_button"})
        except: pass

        xml = device.get_xml()
        elems = device.find_elements({'class':"android.view.ViewGroup", "clickable":"true"}, xml)
        for n in range(1, len(elems), 2):
            # click bell icon
            util.tap_on_nth(device, {'class':"android.view.ViewGroup", "clickable":"true"}, n, xml)
            sleep(1)
            # click unsubscribe
            device.tap((300, 1500))
            sleep(1)


        intervention_data = []
        count = 0

        # for 1000 videos
        for iter in tqdm(range(1000)):

            # restart every 50 videos to refresh app state
            if iter % 20 == 0:
                restart_app(device)
                util.tap_on(device, attrs={'content-desc': 'Shorts', 'class': "android.widget.Button"})

            # break if success
            if count > PARAMETERS["intervention_phase_n"]:
                print('breaking',count)
                break
        
            # check for any flow disruptions first
            #util.check_disruptions(device)
            
            # watch short for a certain time
            sleep(1)

            

            xml = device.get_xml()
            text_elems = device.find_elements({'content-desc': re.compile('.+')}, xml)
            text_elems += device.find_elements({'text': re.compile('.+')}, xml)

            # build row
            row = {}
            for column_id, elem in enumerate(text_elems):
                key = elem['resource-id']
                if key.strip() == '':
                    key = 'col_%s' % column_id
                text = elem['content-desc']
                if text.strip() == '':
                    text = elem['text']
                if text == '':
                    continue
                row[key] = text
                
                if elem['resource-id'] == 'com.google.android.youtube:id/reel_main_title' and classify(query, text):
                    count += 1
                    row['Intervened'] = True
                    row['Intervention'] = intervention
                    print(text)

                    #longtap
                    device.longtap()
                    sleep(1)

                    # click on Not intereseted
                    try: util.tap_on(device, {'text': "Don't recommend this channel"})
                    except: util.swipe_up(device)

            intervention_data.append(row)

            # swipe to next video only if did not intervene here
            if not row.get('Intervened'):
                util.swipe_up(device)
            

        return intervention_data
        

    except Exception as e:
        if e == "'NoneType' object is not subscriptable":
            restart_app(device)

    return intervention_data

def Not_Interested_Unfollow(device,query, intervention):
    #need to change



    try:
        if intervention=="Not_Interested_Unfollow":
            pass 
        
        restart_app(device)
        intervention_data = []
        count = 0

        # for 1000 videos
        for iter in tqdm(range(1000)):

            # restart every 50 videos to refresh app state
            if iter % 20 == 0:
                restart_app(device)
                util.tap_on(device, attrs={'content-desc': 'Shorts', 'class': "android.widget.Button"})

            # break if success
            if count > PARAMETERS["intervention_phase_n"]:
                print('breaking',count)
                break
        
            # check for any flow disruptions first
            #util.check_disruptions(device)
            
            # watch short for a certain time
            sleep(1)

            

            xml = device.get_xml()
            text_elems = device.find_elements({'content-desc': re.compile('.+')}, xml)
            text_elems += device.find_elements({'text': re.compile('.+')}, xml)

            # build row
            row = {}
            for column_id, elem in enumerate(text_elems):
                key = elem['resource-id']
                if key.strip() == '':
                    key = 'col_%s' % column_id
                text = elem['content-desc']
                if text.strip() == '':
                    text = elem['text']
                if text == '':
                    continue
                row[key] = text
                
                if elem['resource-id'] == 'com.google.android.youtube:id/reel_main_title' and classify(query, text):
                    count += 1
                    row['Intervened'] = True
                    row['Intervention'] = intervention
                    print(text)

                    #longtap
                    device.longtap()
                    sleep(1)

                    # click on Not intereseted
                    try: util.tap_on(device, {'text': "Don't recommend this channel"})
                    except: util.swipe_up(device)

            intervention_data.append(row)

            # swipe to next video only if did not intervene here
            if not row.get('Intervened'):
                util.swipe_up(device)

                   
        restart_app(device)

        # press on hide to hide content
        try: util.tap_on(device, attrs={'content-desc': 'Subscriptions'})
        except: pass

        try: util.tap_on(device, {'resource-id':"com.google.android.youtube:id/channels_button"})
        except: pass

        xml = device.get_xml()
        elems = device.find_elements({'class':"android.view.ViewGroup", "clickable":"true"}, xml)
        for n in range(1, len(elems), 2):
            # click bell icon
            util.tap_on_nth(device, {'class':"android.view.ViewGroup", "clickable":"true"}, n, xml)
            sleep(1)
            # click unsubscribe
            device.tap((300, 1500))
            sleep(1)

    except Exception as e:
        if e == "'NoneType' object is not subscriptable":
            restart_app(device)

    return intervention_data

def Control():
    pass
        
if __name__ == '__main__':
        args = parse_args()


        driver = ReelsDriver(profile_dir='profiles/%s' % args.n)

        input("Continue?")

        print("Training Phase 2...", util.timestamp())
        training_phase_2_data = training_phase_2(driver, args.q)
        
        print("Testing Phase 1...", util.timestamp())
        testing_phase_1_data = testing(driver)

        print("Saving...", util.timestamp())
        pd.DataFrame(training_phase_2_data).to_csv(f'training_phase_2/{args.q}--{args.i}--{args.n}_tr_p2.csv', index=False)
        pd.DataFrame(testing_phase_1_data).to_csv(f'testing_phase_1/{args.q}--{args.i}--{args.n}_te_p1.csv', index=False)


        if args.i == "Not_Interested":
       
            print("Not Interested Only Intervention...", util.timestamp())
            intervention_data = Not_Interested(driver, args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)
        
        elif args.i == "Unfollow":
            print("Unfollow Only Intervention...", util.timestamp())
            intervention_data = Unfollow(driver, args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)

        elif args.i == "Unfollow_Not_Interested":
            print("Unfollow then Not Interested Intervention...", util.timestamp())
            intervention_data = Unfollow_Not_Interested(driver, args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)

        elif args.i == "Not_Interested_Unfollow":
            print("Not Interested then Unfollow Intervention...", util.timestamp())
            intervention_data = Not_Interested_Unfollow(driver, args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)

        elif args.i == "Control":
            print("Control Intervention")
            intervention_data = Control(driver, args.q, args.i)
            pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}--{args.i}--{args.n}_int.csv', index=False)

        
        print("Testing Phase 2... ", util.timestamp())
        testing_phase_2_data = testing(driver)

        print("Saving...")
    #     pd.DataFrame(intervention_data).to_csv(f'intervention/{args.q}_{credentials.name}.csv', index=False)
    #     pd.DataFrame(testing_phase_2_data).to_csv(f'testing_phase_2/{args.q}_{credentials.name}.csv', index=False)
        
        pd.DataFrame(testing_phase_2_data).to_csv(f'testing_phase_2/{args.q}--{args.i}--{args.n}_te_p2.csv', index=False)