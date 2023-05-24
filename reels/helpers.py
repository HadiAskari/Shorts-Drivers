import re
import json
from selenium.webdriver.common.by import By

with open('css-classes.json') as f:
    css_classes = json.load(f)

class Short:
    def __init__(self, elem=None, url=None):
        self.elem = elem
        self.url = url
        self.shortId = re.search(r'reels/(.*)?/$', url).group(1)
        self.metadata = dict(
            description=extract_description(elem),
            likes=extract_text(elem, 'div', css_classes['likes+comments'], 0),
            comments=extract_text(elem, 'div', css_classes['likes+comments'], 1),
            author=extract_text(elem, 'span', css_classes['author']),
            music=extract_text(elem, 'div', css_classes['music']),
        )
        
    def to_dict(self):
        return dict(
            url=self.url,
            shortId=self.shortId
        ).update(self.metadata)


class ShortUnavailableException(Exception):
    pass

def extract_text(elem, elem_type, css, index=0):
    try: return elem.find_elements(By.XPATH, ".//%s[contains(@class, '%s')]" % (elem_type, css))[index].text
    except: return ''

def extract_description(elem):
    # extract expanded description
    try: 
        elem.find_element(By.XPATH, ".//span[contains(@class, 'x1rg5ohu xsgj6o6 x1c4vz4f x2lah0s xdl72j9 xlej3yl')]").click()
        return elem.find_element(By.XPATH, ".//div[contains(@class, 'x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh xw7yly9 x1uhb9sk xw2csxc x1odjw0f xs83m0k x1c4vz4f xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1')]").text
    except: pass

    # extract non-expanded description
    try: return elem.find_element(By.XPATH, ".//div[contains(@class, 'x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh xw7yly9 x1n2onr6 x1plvlek xryxfnj x1c4vz4f x2lah0s xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1')]").text
    except: pass
    
    return ''