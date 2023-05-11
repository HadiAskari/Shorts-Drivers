import re
from selenium.webdriver.common.by import By
import json
import subprocess

class Short:
    def __init__(self, elem=None, url=None):
        self.elem = elem
        self.url = url
        self.shortId = re.search(r'shorts/(.*)?$', url).group(1)
        try:
            proc = subprocess.run(['./yt-dlp', '-J', self.url], stdout=subprocess.PIPE)
            self.metadata = json.loads(proc.stdout.decode())
        except:
            self.metadata = {}
        
    def to_dict(self):
        return dict(
            url=self.url,
            shortId=self.shortId
        ).update(self.metadata)


class ShortUnavailableException(Exception):
    pass
