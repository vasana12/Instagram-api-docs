import logging
import re
import unicodedata
from contextlib import suppress
from typing import Dict, Any, Optional, List, Tuple
from urllib import request

from manager import Manager
from exceptions import InstabotException
from datetime import datetime

manager = Manager()

class User:
    def __init__(self, username, max_post, max_follower, max_followee, max_comment):
        pass


class Hashtag:
    def __init__(self, keyword, max_top_post, max_recent_post):
        pass



if __name__ == '__main__':
    user = User(username='faker',max_post=9, max_follower=0, max_followee=0, max_comment=0)
    hashtag = Hashtag(keyword='풀무원', max_top_post=9, max_recent_post=0)
