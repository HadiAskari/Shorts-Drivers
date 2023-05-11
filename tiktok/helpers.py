import re

class Short:
    def __init__(self, elem=None, url=None, description=None):
        self.elem = elem
        self.url = url
        search = re.search(".*/(?P<user>@.+?)/video/(?P<videoId>[0-9]+)", url)
        self.shortId = f"{search.group('user')}/{search.group('videoId')}"
        self.description = description

    def to_dict(self):
        return dict(
            url=self.url,
            shortId=self.shortId,
            description=self.description
        )

class ShortUnavailableException(Exception):
    pass