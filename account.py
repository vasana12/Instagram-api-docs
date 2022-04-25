import random
import logging
from datetime import datetime, timedelta

from setting import ACCOUNT_AVAILABLE_INTERVAL_FROM_LAST_LOGIN
from exceptions import NoAccountError

from model import Account


class AccountSetter:
    def __init__(self):
        self._reset()

    def _reset(self):
        self._account = None
        self.username = None
        self.password = None
        self.csrftoken = None
        self.user_agent = None
        self.sessionid = None

    def _set_variables(self):
        self.username = self._account.username if self._account else None
        self.ds_user_id = self._account.session.ds_user_id if self._account else None
        self.csrftoken = self._account.session.csrftoken if self._account else None
        self.user_agent = self._account.user_agent if self._account else None
        self.sessionid = self._account.session.sessionid if self._account else None
        self.password = self._account.password if self._account else None

    def _safe_login(self, query):
        hash = random.randint(0, 999999)
        temp_status = 'picking_%s' % (str(hash))
        no_target = Account.objects(**query).update_one(status=temp_status)
        if no_target < 1:
            raise NoAccountError
        query['status'] = temp_status

        self._account = Account.objects(**query).first()
        logging.warning('Instagram Account logged-in : %s' % self._account.username)
        self._account.status = 'login'
        now = datetime.utcnow()
        self._account.last_login = now
        self._account.update(status='login', last_login=now)
        self._set_variables()

    def load(self, username):
        query = {'username': username}
        self._safe_login(query)

    def load_one(self):
        max_dt_last_login = datetime.utcnow() - timedelta(hours=ACCOUNT_AVAILABLE_INTERVAL_FROM_LAST_LOGIN)
        query = {"status": "available", "mobile_session": True, "last_login__lt": max_dt_last_login}
        self._safe_login(query)

    def release_error(self):
        self._account.update(status='challenge_required')
        self._reset()

    def release(self):
        self._account.update(status='available')
        self._reset()

    def update(self, **kwargs):
        self._account.update(**kwargs)

    def insert(self,**kwargs):
        self._account.insert(**kwargs)

if __name__ == '__main__' :
    '''
    test
    '''
    account = AccountSetter()
    account.load(username="send_direct_items")
    account.update()



