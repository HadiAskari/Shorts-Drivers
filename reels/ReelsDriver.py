from selenium.webdriver import ChromeOptions, Firefox, FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from time import sleep
from helpers import Short
from pyvirtualdisplay import Display
import undetected_chromedriver as uc

class ReelsDriver:

    def __init__(self, browser='chrome', profile_dir=None, use_virtual_display=False, headless=False, verbose=False):

        if use_virtual_display:
            display = Display(size=(1920,1080))
            display.start()

        if browser == 'chrome':
            self.driver = self.__init_chrome(profile_dir, headless)
        elif browser == 'firefox':
            self.driver = self.__init_firefox(profile_dir, headless)
        else:
            raise Exception("Invalid browser", browser)

        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(10)
        self.verbose = verbose

    def close(self):
        self.driver.close()

    def play(self, video, duration=5):
        # this function returns when the video starts playing
        try:
            self.__click(video)
            sleep(duration)
        except WebDriverException as e:
            self.__log(e)

    def next_short(self):
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_DOWN)
        sleep(0.5)

    def get_current_short(self):
        ancestor = self.driver.find_element(By.XPATH, '//img[@class="xwzpupj x10l6tqk x1bs05mj x19991ni x1d8287x x5yr21d xuzhngd"]/ancestor::div[contains(@class, "x1bhewko")]')
        return Short(url=self.driver.current_url, elem=ancestor)

    def positive_signal(self):
        ancestor = self.driver.find_element(By.XPATH, '//img[@class="xwzpupj x10l6tqk x1bs05mj x19991ni x1d8287x x5yr21d xuzhngd"]/ancestor::div[contains(@class, "x1bhewko")]')

        try:
            like_button = ancestor.find_element(By.XPATH, ".//div[contains(@class, 'x6s0dn4 x1ypdohk x78zum5 xdt5ytf xieb3on')]")
            if like_button.find_element(By.TAG_NAME, 'svg').get_attribute('aria-label') == 'Like':
                like_button.click()
        except: pass

    def negative_signal(self):
        # find ancestor
        ancestor = self.driver.find_element(By.XPATH, '//img[@class="xwzpupj x10l6tqk x1bs05mj x19991ni x1d8287x x5yr21d xuzhngd"]/ancestor::div[contains(@class, "x1bhewko")]')
        # click on more
        ancestor.find_elements(By.XPATH, './/div[@class="x78zum5 x6s0dn4 x1chd833"]')[-1].click()
        # click on report
        self.driver.find_element(By.XPATH, '//button[text()="Report"]').click()
        # click on i don't like it
        self.driver.find_element(By.XPATH, '//div[text()="I just don\'t like it"]').click()        
        # click on close
        self.driver.find_element(By.XPATH, '//button[text()="Close"]').click()
        # regain focus
        self.driver.find_element(By.TAG_NAME, 'body').click()

    def goto_homepage(self):
        self.driver.get('https://www.instagram.com/reels')

    def goto_shorts(self):
        self.goto_homepage()
        # regain focus
        self.driver.find_element(By.TAG_NAME, 'body').click()

    
    def subscribe(self, url):
        self.driver.get(url)
        try: self.driver.find_element(By.XPATH, '//div[text()="Follow"]').click()
        except: pass


    def unfollow_all_accounts(self):
        self.goto_homepage()
        # click on profile button
        menubar = self.driver.find_element(By.XPATH, ".//div[@class='xh8yej3 x1iyjqo2']")
        menubar.find_element(By.XPATH, './/div[text()="Profile"]').click()

        # wait for profile to load
        WebDriverWait(self.driver, 10).until(EC.title_contains('| Instagram'))

        while True:
            # refresh the page
            self.driver.refresh()
            # click on following button
            following_button = self.driver.find_element(By.XPATH, '//a[contains(text(), " following")]')
            if following_button.text == '0 following':
                break
            # click on following button
            following_button.click()
            # find following buttons and unfollow
            unfollow_buttons = self.driver.find_elements(By.XPATH, '//button[@class="_acan _acap _acat _aj1-"]')
            # unfollow each page
            for unfollow_button in unfollow_buttons:
                unfollow_button.click()
                self.driver.find_element(By.XPATH, '//button[text()="Unfollow"]').click()

    def save_screenshot(self, filename):
        return self.driver.save_screenshot(filename)
    
    def login(self, username, password):
        self.driver.get('https://www.instagram.com/accounts/login/')
        self.driver.find_element(By.XPATH, '//input[@name="username"]').send_keys(username)
        self.driver.find_element(By.XPATH, '//input[@type="password"]').send_keys(password)
        sleep(5)
        self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        sleep(10)
        
    ## helper methods
    def __log(self, message):
        if self.verbose:
            print(message)

    def __click(self, video):
        if type(video) == Short:
            try:
                # try to click the element using selenium
                self.__log("Clicking element via Selenium...")
                video.elem.click()
                return
            except Exception as e:
                try:
                    # try to click the element using javascript
                    self.__log("Failed. Clicking via Javascript...")
                    self.driver.execute_script('arguments[0].click()', video.elem)
                except:
                    # js click failed, just open the video url
                    self.__log("Failed. Loading video URL...")
                    self.driver.get(video.url)
        elif type(video) == str:
            self.driver.get(video)
        else:
            raise ValueError('Unsupported video parameter!')
    
    def __init_chrome(self, profile_dir, headless):
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')

        if profile_dir is not None:
            options.add_argument('--user-data-dir=%s' % profile_dir)
        if headless:
            options.add_argument('--headless')

        driver = uc.Chrome(options=options, version_main=112, driver_executable_path='./chromedriver')

        return driver

    def __init_firefox(self, profile_dir, headless):
        options = FirefoxOptions()
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        if profile_dir is not None:
            pass
        if headless:
            options.add_argument('--headless')

        return Firefox(options=options)

