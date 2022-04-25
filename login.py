from datetime import datetime
import hashlib
import hmac
import json
import random
import time
import hashlib
import uuid
from typing import Optional

from m_raw_account import RawAccountSetter

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
import six.moves.urllib as urllib
import logging
import requests
import requests.utils
from m_proxy import ProxySetter
from device import DeviceSetter
from m_config import ConfigSetter
from account import AccountSetter
from model import *


class AccoutBuilder:
    session = requests.Session()
    FORMAT = '%(module)s.%(funcName)s - %(message)s - %(levelname)s - %(asctime)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger(__name__)
    if logger.hasHandlers():
        # Logger is already configured, remove all handlers
        logger.handlers = []
    logger.setLevel(logging.DEBUG)
    logger = logger
    last_response = None
    last_json = None

    def __init__(self,username=None):
        self.username = username
        self.set_raw_account()
        self.set_proxy()
        self.set_device()
        self.set_uuids()
        self.set_config()
        self.set_header()
        # self.raw_account : RawAccountSetter= Optional[None]
        # self.proxy : ProxySetter = Optional[None]
        # self.device : DeviceSetter = Optional[None]
        # self.config : ConfigSetter= Optional[None]

    @property
    def cookie_dict(self):
        return self.session.cookies.get_dict()
    @property
    def token(self):
        return self.cookie_dict.get("csrftoken")

    @staticmethod
    def get_default_header():
        headers = {
            "X-IG-App-Locale": "en_US",
            "X-IG-Device-Locale": "en_US",
            "X-Pigeon-Session-Id": "21aa671b-a5f3-4093-8ec2-0c98420675e1",
            "X-Pigeon-Rawclienttime": str(round(time.time() * 1000)),
            "X-IG-Connection-Speed": "-1kbps",
            "X-IG-Bandwidth-Speed-KBPS": str(random.randint(7000, 10000)),
            "X-IG-Bandwidth-TotalBytes-B": str(random.randint(500000, 900000)),
            "X-IG-Bandwidth-TotalTime-MS": str(random.randint(50, 150)),
            "X-IG-Prefetch-Request": "foreground",
            "X-Bloks-Version-Id": "0a3ae4c88248863609c67e278f34af44673cff300bc76add965a9fb036bd3ca3",
            "X-IG-WWW-Claim": "0",
            "X-MID": "XkAyKQABAAHizpYQvHzNeBo4E9nm",
            "X-Bloks-Is-Layout-RTL": "false",
            "X-Bloks-Enable-RenderCore": "false",
            # TODO get the uuid from api_login here
            # "X-IG-Device-ID": "{uuid}",
            # TODO get the device_id from api_login here
            # "X-IG-Android-ID": "{device_id}",
            "X-IG-Connection-Type": "WIFI",
            "X-IG-Capabilities": "3brTvwE=",
            "X-IG-App-ID": "567067343352427",
            "X-IG-App-Startup-Country": "US",
            "Accept-Language": "en-US",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Encoding": "gzip, deflate",
            "Host": "i.instagram.com",
            "X-FB-HTTP-Engine": "Liger",
            "Connection": "close",
        }
        return headers

    @staticmethod
    def generate_UUID(uuid_type):
        generated_uuid = str(uuid.uuid4())
        if uuid_type:
            return generated_uuid
        else:
            return generated_uuid.replace("-", "")

    @staticmethod
    def get_seed(*args):
        m = hashlib.md5()
        m.update(b"".join([arg.encode("utf-8") for arg in args]))
        return m.hexdigest()

    @staticmethod
    def generate_device_id(seed):
        volatile_seed = "12345"
        m = hashlib.md5()
        m.update(seed.encode("utf-8") + volatile_seed.encode("utf-8"))
        return "android-" + m.hexdigest()[:16]


    def generate_all_uuids(self):
        phone_id = self.generate_UUID(uuid_type=True)
        uuid = self.generate_UUID(uuid_type=True)
        client_session_id = self.generate_UUID(uuid_type=True)
        advertising_id = self.generate_UUID(uuid_type=True)
        device_id = self.generate_device_id(self.get_seed(self.username, self.password))
        uuids = {

                    "phone_id": phone_id,
                    "uuid": uuid,
                    "client_session_id": client_session_id,
                    "advertising_id": advertising_id,
                    "device_id": device_id
        }
        return uuids

    def generate_signature(self, data):
        body = (
            hmac.new(
                self.ig_sig_key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
            ).hexdigest()
            + "."
            + urllib.parse.quote(data)
        )
        signature = "signed_body={body}&ig_sig_key_version={sig_key}"

        return signature.format(sig_key= self.sig_key_version, body=body)

    def set_raw_account(self):
        raw_account = RawAccountSetter()
        self.raw_account = raw_account
        query = {}
        if self.username:
            query.update(username=self.username)
        raw_account.load(query)
        self.username = raw_account.username
        self.password = raw_account.password
        self.logger.info(f"set_raw_account:{self.username}/{self.password}")

    def set_proxy(self):
        proxy = ProxySetter()
        proxy.load({})
        self.proxy = f"http://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
        self.logger.info(f"set_proxy:{self.proxy}")

    def set_device(self):
        device = DeviceSetter()
        device.load({})
        self.device = device
        self.logger.info(f"set_device:{self.device.to_dict()}")

    def set_uuids(self):
        self.uuids = self.generate_all_uuids()
        self.logger.info(f"set_uuids:{self.uuids}")

    def set_config(self):
        config = ConfigSetter()
        config.load({})
        self.api_domain = config.api_domain
        self.api_url = config.api_url
        self.ig_sig_key = config.ig_sig_key
        self.sig_key_version = config.sig_key_version
        self.logger.info(f"set_config:{self.api_domain}")

    def set_header(self):
        self.session.headers.update(self.get_default_header())
        self.device.load({})
        self.session.headers.update({"User-Agent": self.device.user_agent})
        self.logger.info(f"set_header")

    def build(self):
        print(self.device)
        self.get_prefill_candidates()

        if self.login():
            cookie = requests.utils.dict_from_cookiejar(self.session.cookies)

            raw_data = {}
            raw_data.update(username=self.username,
                            password=self.password,
                            channel="instagram",
                            status="available",
                            last_login=datetime.now(),
                            session=cookie,
                            mobile_session= True,
                            uuids=self.uuids,
                            device_setting=self.device.to_dict(),
                            user_agent=self.device.user_agent
                            )
            Account(**raw_data).save()
            self.raw_account.update(status="setting_done")

    def get_prefill_candidates(self):
        data = {
            "android_device_id": self.uuids["device_id"],
            "phone_id": self.uuids["phone_id"],
            "usages": '["account_recovery_omnibox"]',
            "device_id": self.uuids["device_id"],
        }
        self.logger.debug(f"data:{data}")
        data = json.dumps(data)
        return self.send_request(f"{self.api_url}accounts/get_prefill_candidates/", post=data, with_signature=True)

    def login_success(self):
        pass

        # setting_info = read_account_setting_info_from_db(self.username, self.password)
        # cookie = requests.utils.dict_from_cookiejar(self.session.cookies)
        # setting_info["username"], setting_info["password"], setting_info["cookie"] = self.username, self.password, cookie
        # self.logger.info(f"{self.username}/{self.password} success - > account collection")
        # msg = f"SETTING INFO : COOKIE \n- {cookie} - " \
        #       f"TIMING, DEVICE and ...\n- user-agent={setting_info['user_agent']}\n- phone_id={setting_info['uuids']['phone_id']}\n- " \
        #       f"uuid={setting_info['uuids']['uuid']}\n- client_session_id={setting_info['uuids']['client_session_id']}\n- device_id={setting_info['uuids']['device_id']}"
        # self.logger.debug(msg)

        return True

    def login_failed(self):
        pass

    def login(self):
        self.logger.info(f"login_trial")
        data = json.dumps({
            "jazoest": "22264",
            "country_codes": '[{"country_code":"1","source":["default"]}]',
            "phone_id": self.uuids["phone_id"],
            "_csrftoken": self.token,
            "username": self.username,
            "adid": "",
            "guid": self.uuids["uuid"],
            "device_id": self.uuids["device_id"],
            "google_tokens": "[]",
            "password": self.password,
            # "enc_password:" "#PWD_INSTAGRAM:4:TIME:ENCRYPTED_PASSWORD"
            "login_attempt_count": "0",
        })

        return self.send_request(f"{self.api_url}accounts/login/", post=data, with_signature=True)

    def send_request(self, url, post, with_signature, extra_sig=None, timeout=30, waiting_429=None):
        method = "POST" if post else "GET"
        if post is not None:  # POST
            if with_signature:
                post = self.generate_signature(post)  #
                if extra_sig is not None and extra_sig != []:
                    post += "&".join(extra_sig)
            try:
                response = self.session.post(url, data=post,timeout=timeout)
            except Exception as e:
                self.logger.debug(f"error:{e}")
                return False
        else:
            response = self.session.get(url,timeout=timeout)
            return response

        self.last_response = response
        self.logger.info(f"{method} to endpoint:{url} returned response: {response.status_code}")
        if response.status_code == 200:
            try:
                self.last_json = json.loads(response.text)
                return True
            except JSONDecodeError:
                self.logger.debug(f"response.status_code - {response.status_code}:JSONDecodeError")
                return False
        else:
            self.logger.debug(f"Responsecode indicated error; returned response : {response.status_code} response content: {response.content[0:100]}")
            return False

account_builder = AccoutBuilder()
print(account_builder.device)
account_builder.build()

