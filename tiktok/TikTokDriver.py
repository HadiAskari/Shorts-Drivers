from socket import timeout
import undetected_chromedriver as uc
from selenium.webdriver import Chrome, ChromeOptions, Firefox, FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from time import sleep
from helpers import Short
from pyvirtualdisplay import Display
from urllib.parse import quote_plus
import re

class TikTokDriver:

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
        self.verbose = verbose

    def close(self):
        self.driver.close()

    def search_and_watch(self, query, num=10, duration=30):
        # go to homepage and type in search query
        self.goto_homepage()

        # type in search query
        self.driver.find_element(By.XPATH, '//input[@name="q"]').send_keys(query)
        self.driver.find_element(By.XPATH, '//input[@name="q"]').send_keys(Keys.ENTER)

        # click on top result
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@data-e2e="search_top-item"]'))
        )
        self.driver.find_element(By.XPATH, '//div[@data-e2e="search_top-item"]').click()

        for i in range(num):
            print("Watching %s / %s video..." % (i, num))

            # watch for some time
            sleep(duration)
            
            # like and follow
            try: self.driver.find_element(By.XPATH, '//span[@data-e2e="browse-like-icon"]').click()
            except: pass
            try: self.driver.find_element(By.XPATH, '//button[text()="Follow"]').click()
            except: pass

            # scroll to next video
            sleep(5)
            self.driver.find_element(By.XPATH, '//button[@data-e2e="arrow-right"]').click()

        # # load video search results
        # self.driver.get('https://tiktok.com/search/video?q=%s' % quote_plus(query))

        # sleep(3)

        # # scroll page to load more results
        # for _ in range(scroll_times):
        #     el = self.driver.find_element(By.XPATH, '//button[text()="Load more"]')
        #     if el is not None:
        #         el.click()
        #     sleep(1)

        # results = []
        # sleep(0.5)

        # # collect video-like tags from homepage
        # videos = self.driver.find_elements(By.TAG_NAME, 'a')

        # # identify actual videos from tags
        # for video in videos:
        #     href = video.get_attribute('href')
        #     if href is not None and re.match(r'https://www.tiktok.com/@.*?/video/[0-9]+', href) is not None:
        #         try:
        #             desc = video.find_element(By.TAG_NAME, 'img').get_attribute('alt')
        #             results.append(Short(video, href, desc))
        #         except:
        #             pass
        # return results

    def play(self, video, duration=5):
        # this function returns when the video starts playing
        try:
            self.__click(video)
            sleep(duration)
        except WebDriverException as e:
            self.__log(e)

    def next_short(self):
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_DOWN)
        sleep(1)

    def get_current_short(self):
        # click on video
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.TAG_NAME, 'video'))
        )

        self.driver.find_element(By.TAG_NAME, 'video').click()

        # wait until url changes
        WebDriverWait(self.driver, 10).until(
            EC.url_contains('/video/')
        )

        # get url
        url = self.driver.current_url
        url = url.split('?')[0]

        # get description
        desc = self.driver.find_element(By.CSS_SELECTOR, '[data-e2e="browse-video-desc"]').text

        # close video
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)

        return Short(url=url, description=desc)
    
    def login(self, email, password):
        # open homepage
        self.goto_homepage()

        # start login work flow
        ## click on login button
        try: self.driver.find_element(By.XPATH, '//button[text()="Log in"]').click()
        except: pass
        sleep(5)
        ## use phone / email / username button
        self.driver.find_element(By.XPATH, '//p[text()="Use phone / email / username"]').click()
        sleep(5)
        ## log in with email / username
        self.driver.find_element(By.XPATH, '//a[text()="Log in with email or username"]').click()
        sleep(5)
        ## fill in username and password
        self.driver.find_element(By.XPATH, '//input[@name="username"]').send_keys(email)
        sleep(5)
        self.driver.find_element(By.XPATH, '//input[@placeholder="Password"]').send_keys(password)
        sleep(5)
        self.driver.find_element(By.XPATH, '//button[@type="submit" and text()="Log in"]').click()
        sleep(5)
        


    def goto_homepage(self):
        self.driver.get('https://www.tiktok.com')

    def goto_shorts(self):
        self.goto_homepage()

    def save_screenshot(self, filename):
        return self.driver.save_screenshot(filename)

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
        return uc.Chrome(executable_path='./chromedriver', options=options)

    def __init_firefox(self, profile_dir, headless):
        options = FirefoxOptions()
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        if profile_dir is not None:
            pass
        if headless:
            options.add_argument('--headless')
        return Firefox(options=options)

