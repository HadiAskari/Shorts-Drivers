import re
from selenium.webdriver.common.by import By
import json

with open('css-classes.json') as f:
    css_classes = json.load(f)

class Short:
    def __init__(self, elem=None, url=None):
        self.elem = elem
        self.url = url
        self.shortId = re.search(r'reels/(.*)?/$', url).group(1)
        self.metadata = dict(
            description=extract_text(elem, 'div', css_classes['description']),
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