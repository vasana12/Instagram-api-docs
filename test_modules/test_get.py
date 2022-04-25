from account import InstagramAccount
from connection import Session
from scrapper import Scrapper
import logging

FORMAT = '%(module)s.%(funcName)s - %(message)s - %(levelname)s - %(asctime)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
if logger.hasHandlers():
    # Logger is already configured, remove all handlers
    logger.handlers = []
logger.setLevel(logging.DEBUG)

def setting():
    account = InstagramAccount()
    account.load_one_for_crawling_tmp(username="kremer7bkdianshin")

    session = Session()
    session.ds_user_id = account.ds_user_id
    session.csrftoken = account.csrftoken
    session.user_agent = account.user_agent
    session.sessionid = account.sessionid
    session.username = account.username
    scrapper = Scrapper(session)
    return scrapper

### test modules
username= "faker"
userid=42480603254
hashtag = "potato"
scrapper = setting()


def test_get_user(scrapper, username):
    return scrapper.get_user(username=username)

def test_get_user_posts(scrapper,userid):
    for i in scrapper.get_user_posts(userid=userid):
        logger.debug(i)

def test_get_user_followers(scrapper,userid):
    for i in scrapper.get_user_followers(userid=userid):
        logger.debug(i)

def test_get_user_followees(scrapper,userid):
    for i in scrapper.get_user_followees(userid=userid):
        logger.debug(i)

def test_get_hashtag(scrapper, hashtag):
    return scrapper.get_hashtag(hashtag=hashtag)

def test_get_hashtag_recent_posts(scrapper, hashtag):
    for i in scrapper.get_hashtag_recent_posts(hashtag=hashtag):
        logger.debug(i)

def test_get_hashtag_top_posts(scrapper, hashtag):
    for i in scrapper.get_hashtag_top_posts(hashtag=hashtag):
        logger.debug(i)
