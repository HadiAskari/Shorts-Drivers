from ReelsDriver import ReelsDriver
from selenium.webdriver.common.by import By

# load the driver
driver = ReelsDriver(browser='chrome', verbose=True, profile_dir='profiles/test')


# driver.login('christopher_wright_743@youtubeaudit.com', 'Yuio1234!')
driver.goto_shorts()

