from TikTokDriver import TikTokDriver
import os
from time import sleep
from shutil import rmtree
import json

keyword = 'abortion'
input()
# load the driver
driver = TikTokDriver(use_virtual_display=False, profile_dir='profiles/andrew_newman215')


input("Continue?")
# driver.goto_homepage()

# # search and watch video
driver.search_and_watch(keyword, 10, 5)
