from account import InstagramAccount
from connection import Session
from scrapper import Scrapper
import logging

from account import InstagramAccount
from connection import Session
from model import Hashtag, User


class Manager :
    def __init__(self):
        self._account = None
        self._session = None
        self._scrapper = None
        self.n_request = None
        self.load_account()

    def load_account(self, username=None):
        self._account.release()
        self.n_request = 0

        if username:
            self._account.load(username)
        else :
            self._account.load_one()

        self._session = Session(account=self._account)
        self._scrapper = Scrapper(self._session)


    def release_account(self):
        if self._account:
            self._account.release()
        else:
            pass

    def get_hashtag(self, keyword):
        return self._scrapper.get_hashtag(hashtag=keyword)

    def get_hashtag_top_posts(self, keyword):
        return self._scrapper.get_hashtag_top_posts(hashtag=keyword)

    def get_hashtag_recent_posts(self, keyword):
        return self._scrapper.get_hashtag_recent_posts(hashtag=keyword)

    def get_user(self, username):
        return self._scrapper.get_user(username=username)

    def get_user_posts(self, userid):
        return self._scrapper.get_user_posts(userid=userid)

    def get_user_followers(self, userid):
        return self._scrapper.get_user_followers(userid=userid)

    def get_user_followees(self, userid):
        return self._scrapper.get_user_followees(userid=userid)


class TestManager(Manager):
    def __init__(self):
        self._account = InstagramAccount()
        self._account.load(username="kremer7bkdianshin")
        self._session = Session(account=self._account)
        self._scrapper = Scrapper(self._session)


if __name__ == '__main__':
    manager = TestManager()
    user = manager.get_user("faker")
    hashtag = manager.get_hashtag("테슬라")
    print(user)
