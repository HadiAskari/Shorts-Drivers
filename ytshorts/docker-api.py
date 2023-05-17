from argparse import ArgumentParser
import docker
from time import sleep
import os
import pandas as pd

# change this to your own ID
IMAGE_NAME = 'hadi/ytshorts'
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
USERNAME = os.getuid()

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--build', action="store_true", help='Build docker image')
    parser.add_argument('--run', action="store_true", help='Run all docker containers')
    parser.add_argument('--simulate', action="store_true", help='Only generate arguments but do not start containers')
    parser.add_argument('--max-containers', default=10, type=int, help="Maximum number of concurrent containers")
    parser.add_argument('--run-file', required=True, help='Path to file containing run information')
    parser.add_argument('--sleep-duration', default=60, type=int, help="Time to sleep (in seconds) when max containers are reached and before spawning additional containers")
    args = parser.parse_args()
    return args, parser

def build_image():
    # get docker client and build image
    client = docker.from_env()

    # build the image from the Dockerfile
    #   -> tag specifies the name
    #   -> rm specifies that delete intermediate images after build is completed
    _, stdout = client.images.build(path='.', tag=IMAGE_NAME, rm=True)
    for line in stdout:
        if 'stream' in line:
            print(line['stream'], end='')
    
def get_mount_volumes():
    # binds "/output" on the container -> "OUTPUT_DIR" actual folder on disk
    return { OUTPUT_DIR: { "bind": "/output" } }

def get_container_list(client):
    for container in client.containers.list():
        for tag in container.image.tags:
            if IMAGE_NAME in tag:
                yield container

def max_containers_reached(client, max_containers):
    try:
        return len(list(get_container_list(client))) >= max_containers
    except Exception as e:
        return True

def spawn_containers(args):
    # get docker client
    client = docker.from_env()
    
    # spawn containers for each user
    count = 0
    
    # load runs file
    runs = pd.read_csv(args.run_file)

    # load completed runs
    with open('completed_runs.txt') as f:
        completed_runs = set(f.read().strip().split('\n'))

    for run in runs.itertuples():

        # check if not already completed
        if run.n in completed_runs:
            continue
        
        # spawn container if it's not a simulation
        if not args.simulate:
            print("Spawning container...")

            # set outputDir as "/output"
            command = ['python', 'main.py', '--q', run.q, '--i', run.i, '--n', run.n, '--outputDir', '/output']

            # check for running container list
            while max_containers_reached(client, args.max_containers):
                # sleep for a minute if maxContainers are active
                print("Max containers reached. Sleeping...")
                sleep(args.sleep_duration)
            
            # run the container
            try:
                client.containers.run(IMAGE_NAME, command, volumes=get_mount_volumes(), shm_size='512M', remove=False, detach=True)
                with open('completed_runs.txt', 'a') as f:
                    f.write(run.n + '\n')
            except Exception:
                pass
            
        # increment count of containers
        count += 1

    print("Total containers spawned:", count)

def main():

    args, parser = parse_args()

    if args.build:
        print("Starting docker build...")
        build_image()
        print("Build complete!")

    if args.run:
        spawn_containers(args)

    if not args.build and not args.run:
        parser.print_help()


if __name__ == '__main__':
    main()
