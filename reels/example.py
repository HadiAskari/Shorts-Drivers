from ReelsDriver import ReelsDriver

# load the driver
driver = ReelsDriver(browser='chrome', verbose=True, profile_dir='profiles/test')


driver.goto_shorts()


