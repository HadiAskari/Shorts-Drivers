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
import undetected_chromedriver as uc

class YTShortDriver:

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

    def search(self, query, scroll_times=0):
        # load video search results
        self.driver.get('https://www.youtube.com/results?search_query=%%23shorts %s' % quote_plus(query))

        # scroll page to load more results
        for _ in range(scroll_times):
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            sleep(0.2)

        results = []
        sleep(0.5)

        # collect video-like tags from homepage
        videos = self.driver.find_elements(By.XPATH, '//div[@id="contents"]/ytd-video-renderer')

        # identify actual videos from tags
        for video in videos:
            a = video.find_elements(By.TAG_NAME, 'a')[0]
            href = a.get_attribute('href')
            if href is not None and href.startswith('https://www.youtube.com/shorts'):
                results.append(Short(a, href))
        return results

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
        WebDriverWait(self.driver, 10).until(EC.url_contains('/shorts/'))
        return Short(url=self.driver.current_url)

    def positive_signal(self):
        ancestor = self.driver.find_element(By.XPATH, '//video/ancestor::ytd-reel-video-renderer')
        try:
            like_button = ancestor.find_element(By.XPATH, './/ytd-toggle-button-renderer[@id="like-button"]')
            if like_button.find_element(By.TAG_NAME, 'button').get_attribute('aria-pressed') == 'false':
                like_button.click()
        except: pass

    def negative_signal(self):
        ancestor = self.driver.find_element(By.XPATH, '//video/ancestor::ytd-reel-video-renderer')
        try:
            # dont recommend channel
            ancestor.find_element(By.XPATH, './/div[@id="menu-button"]').click()
            self.driver.find_element(By.XPATH, '//yt-formatted-string[text()="Don\'t recommend this channel"]').click()
        except: pass

    def unfollow_all_accounts(self):
        # open subscriptions page
        self.driver.get('https://www.youtube.com/feed/channels')
        # get all subscription buttons
        subscriptions = self.driver.find_elements(By.TAG_NAME, 'ytd-subscribe-button-renderer')
        # unsubscribe from buttons
        for subscription in subscriptions:
            # click button
            subscription.click()
            # click unsubscribe
            self.driver.find_element(By.XPATH, '//yt-formatted-string[text()="Unsubscribe"]').click()
            # confirm unsubscribe
            self.driver.find_element(By.XPATH, '//button[@aria-label="Unsubscribe"]').click()


    def subscribe(self, url):
        self.driver.get(url)

        subscription = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'ytd-subscribe-button-renderer'))
        )

        # get all subscription buttons
        #subscriptions = self.driver.find_elements(By.TAG_NAME, 'ytd-subscribe-button-renderer')
        # for subscription in subscriptions:
        # click button
        subscription.click()

    def login(self, username, password):
        # go to the homepage first
        self.goto_homepage()

        # click on signin
        sign_in = self.driver.find_elements(By.XPATH, '//a[@aria-label="Sign in"]')
        
        if len(sign_in) == 0:
            # no sign in button => already signed in
            return

        # click sign in button
        sign_in[0].click()

        # type in email
        self.driver.find_element(By.XPATH, '//input[@type="email"]').send_keys(username)
        sleep(3)

        # click on next
        self.driver.find_element(By.XPATH, '//span[text()="Next"]').click()
        sleep(3)

        # type in password
        self.driver.find_element(By.XPATH, '//input[@type="password"]').send_keys(password)
        sleep(3)

        # click on next
        self.driver.find_element(By.XPATH, '//span[text()="Next"]').click()
        sleep(3)

        # click on not now if asking for address
        try: self.driver.find_element(By.XPATH, '//span[text()="Not now"]').click()
        except: pass


    def goto_homepage(self):
        self.driver.get('https://www.youtube.com')

    def goto_shorts(self):
        self.goto_homepage()
        sections = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'sections'))
        )
        sleep(0.5)
        sections = sections.find_elements(By.TAG_NAME, 'a')
        for section in sections:
            if 'Shorts' in section.text:
                section.click()
                return sleep(0.5)
        raise Exception()

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
        options = uc.ChromeOptions()
        options.add_argument('--window-size=1920,1080')

        if headless:
            options.headless = headless

        return uc.Chrome(options=options, version_main=112, driver_executable_path='./chromedriver', user_data_dir=profile_dir)

    def __init_firefox(self, profile_dir, headless):
        options = FirefoxOptions()
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        if profile_dir is not None:
            pass
        if headless:
            options.add_argument('--headless')

        return Firefox(options=options)

