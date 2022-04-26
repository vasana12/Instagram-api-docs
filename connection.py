from typing import Any, Callable, Dict, Iterator, List, Optional, Union

import requests
import requests.utils
import copy


def default_user_agent() -> str:
    return 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
           '(KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'


def default_headers(empty_session_only: bool = False) -> Dict[str, str]:
    """Returns default HTTP header we use for requests.

    Args:
        empty_session_only (bool): if true, we remove Host, Origin, X-Instagram-AJAX, X-Requested-With
    """

    headers = {'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive',
               'Content-Length': '0',
               'Host': 'www.instagram.com',
               'Origin': 'https://www.instagram.com',
               'Referer': 'https://www.instagram.com/',
               'User-Agent': default_user_agent(),
               'X-Instagram-AJAX': '1',
               'X-Requested-With': 'XMLHttpRequest'}

    if empty_session_only:
        del headers['Host']
        del headers['Origin']
        del headers['X-Instagram-AJAX']
        del headers['X-Requested-With']
    return headers


def default_login_headers():
    headers = {'authority': 'i.instagram.com',
               'sec-ch-ua': '^\\^',
               'x-ig-www-claim': 'hmac.AR1zEkyp_49MJj9gFdNddIdOHHRRXiLFKjcUAM8aCZpTodan',
               'sec-ch-ua-mobile': '?0',
               'x-instagram-ajax': '038c8e332b43',
               'content-type': 'application/x-www-form-urlencoded',
               'accept': '*/*',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
               'x-asbd-id': '437806',
               'x-csrftoken': '',
               'x-ig-app-id': '936619743392459',
               'origin': 'https://www.instagram.com',
               'sec-fetch-site': 'same-site',
               'sec-fetch-mode': 'cors', 'sec-fetch-dest': 'empty',
               'referer': 'https://www.instagram.com/',
               'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'}
    return headers


def custom_http_headers(LoginCSRFtoken):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/accounts/login/",
        "x-csrftoken": LoginCSRFtoken
    }
    return headers


def default_cookies() -> Dict['str', 'str']:
    cookies = {'sessionid': '',
               'ig_pr': '1',
               'ig_vw': '1920',
               'ig_cb': '1',
               'csrftoken': '',
               's_network': '',
               'ds_user_id': '',
               'ig_did': '0976F080-548B-4797-9541-59CD87106A52',
               'mid': 'X2V5XwALAAFXnLmEccKvAiyIVpVL',
               'ig_nrcb': '1',
               'shbts': '1623064813.0255795',
               'rur': 'FTW'}
    return cookies


class Session:
    def __init__(self, account=None):
        self.username = None
        self.reset()
        if account :
            self.load_account(account)

    def reset(self):
        self._session = requests.Session()
        self.headers = default_login_headers()
        self.cookies = default_cookies()
        self.user_agent = default_user_agent()
        self.csrftoken = ''
        self.ds_user_id = ''
        self.sessionid = ''
        self.username = None

    def load_account(self, account):
        self.ds_user_id = account.ds_user_id
        self.csrftoken = account.csrftoken
        self.user_agent = account.user_agent
        self.sessionid = account.sessionid
        self.username = account.username

    @property
    def headers(self):
        return self._session.headers

    @headers.setter
    def headers(self, headers):
        '''
        user-agent 및 cookies 는 header에 입력된 값 보다는 각각의 파라매터에 직접 입력한 값이 우선순위
        '''
        self._session.headers = headers

    @property
    def user_agent(self):
        if 'user-agent' in self._session.headers:
            return self._session.headers['user-agent']
        else:
            return None

    @user_agent.setter
    def user_agent(self, user_agent):
        '''
        user-agent 및 cookies 는 header에 입력된 값 보다는 각각의 파라매터에 직접 입력한 값이 우선순위
        '''
        self._session.headers['user-agent'] = user_agent

    @property
    def cookies(self):
        return self._session.cookies.get_dict()

    @cookies.setter
    def cookies(self, cookies):
        '''
        user-agent 및 cookies 는 header에 입력된 값 보다는 각각의 파라매터에 직접 입력한 값이 우선순위
        '''
        self._session.cookies.update(cookies)

    @property
    def csrftoken(self):
        if 'x-csrftoken' in self._session.headers:
            return self._session.headers['x-csrftoken']
        elif 'csrftoken' in self._session.cookies:
            return self._session.cookies['csrftoken']
        else:
            return None

    @csrftoken.setter
    def csrftoken(self, csrftoken):
        self._session.headers['x-csrftoken'] = csrftoken
        self._session.cookies['csrftoken'] = csrftoken

    @property
    def ds_user_id(self):
        if 'ds_user_id' in self._session.cookies:
            return self._session.cookies['ds_user_id']
        else:
            return None

    @ds_user_id.setter
    def ds_user_id(self, ds_user_id):
        self._session.cookies['ds_user_id'] = ds_user_id

    @property
    def sessionid(self):
        if 'sessionid' in self._session.cookies:
            return self._session.cookies['sessionid']
        else:
            return None

    @sessionid.setter
    def sessionid(self, sessionid):
        self._session.cookies['sessionid'] = sessionid

    def copy(self):
        return copy.deepcopy(self)

    def get(self, url, **kwargs):
        return self._session.get(url=url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self._session.post(url, data=data, json=json, **kwargs)


# if __name__ == '__main__' :
#     '''
#     test
#     '''
#     from account import InstagramAccount
#     import json
#     account = InstagramAccount()
#     username = 'kremer7bkdianshin'
#     account.load(username)
#     print(account.username)
#     session = Session(account)
#     hashtag = '테슬라'
#     host = "www.instagram.com"
#     path = f"explore/tags/{hashtag}/"
#     params = {"__a": 1}
#     resp = session.get('https://{0}/{1}'.format(host, path), params=params, allow_redirects=False)
#     print(json.loads(resp.text))
#     account.release()

