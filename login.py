import json
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
import urllib.parse
import hashlib
import hmac
import logging
import random
import time
import uuid
import requests
from proxy import ProxyManager
from device import DeviceManager
from config import ConfigManager
from raw_account import RawAccountManager

class AccountBuilder:
    """this class makes account available for all circumstances.

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Attributes:
        username (str): username to make available
        session (requests.sesssions.Session): Description of `session`.
        logger (logging.Logger): Description of `logger`.
        last_response (:obj:`None`, optional): Description of `last_response`.
        last_json (:obj:`None`, optional): Description of `last_json`.

    """

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

    def __init__(self, username):
        """Example of docstring on the __init__ method.

        The __init__ method may be documented in either the class level
        docstring, or as a docstring on the __init__ method itself.

        Either form is acceptable, but the two should not be mixed. Choose one
        convention to document the __init__ method and be consistent with it.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            username (str): Description of `username`.
        """
        self.username = username

        config = ConfigManager()
        self.config = config

        device = DeviceManager()
        self.device = device

        proxy = ProxyManager()
        self.proxy = proxy

        self.session.headers.update(self.get_default_header())
        self.session.headers.update({"User-Agent": self.device.user_agent})

        raw_account = RawAccountManager()
        self.raw_account = raw_account

        self.uuids = self.generate_all_uuids()

    @property
    def cookie(self) -> dict:
        self._cookies = self.session.cookies.get_dict()
        return self._cookies

    @cookie.setter
    def cookie(self, cookie_info:dict):
        self._cookies = cookie_info

    @property
    def csrftoken(self) -> str:

        self._csrftoken = self.cookie.get("csrftoken")
        return self._csrftoken

    @csrftoken.setter
    def csrftoken(self, csrftoken:str):
        self._csrftoken = csrftoken

    @property
    def proxy(self) -> ProxyManager:
        """

        Returns:
            proxy.ProxyManager: self._proxy

        Examples:
            this example shows how to get and set proxy

            >>> ### setter
            from proxy import ProxyManager
            proxy = ProxyManager()
            self.proxy = proxy

            >>> ### getter
            self.proxy()
        """

        return self._proxy

    @proxy.setter
    def proxy(self, proxy: ProxyManager):  # setter
        proxy.load({})
        self._proxy = proxy
        # self._proxy = f"http://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"

    @property
    def device(self) -> DeviceManager:
        """device.DeviceManager: set and get device

        Returns:
            device.DeviceManager: self._device

        Examples:
            this example shows how to get and set device

            >>> ### setter
            from device import DeviceManager
            device = DeviceManager()
            self.device = device

            >>> ### getter
            self.device
        """
        return self._device

    @device.setter
    def device(self, device:DeviceManager):
        device.load({})
        self._device = device

    @property
    def config(self) -> ConfigManager:
        """config.ConfigManager: set and get config

        Returns:
            config.ConfigManager : self._config

        Examples:
            this example shows how to get and set config

            >>> ### setter
            from config import ConfigManager
            config = ConfigManager()
            self.config = config

            >>> ### getter
            self.config
        """
        return self._config

    @config.setter
    def config(self, config:ConfigManager):
        config.load({})
        self._config = config

    @property
    def raw_account(self) -> RawAccountManager:
        """raw_account.RawAccountManager: set and get raw_account

                Returns:
                    raw_account.RawAaccountManager : self._raw_account

                Examples:
                    this example shows how to get and set raw_account

                    >>> ### setter
                    from raw_account import RawAccountManager
                    raw_account = RawAccountManager()
                    self.raw_account = raw_account

                    >>> ### getter
                    self.raw_account
                """
        return self._raw_account

    @raw_account.setter
    def raw_account(self, raw_account:RawAccountManager):
        raw_account.load({})
        self._raw_account = raw_account

    @staticmethod
    def get_default_header():
        """
        Returns:
            dict: headers.

        Examples
            this shows default header

            >>>
            import random
            {"X-IG-App-Locale": "en_US",
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
            "Connection": "close"}
        """

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
    def generate_UUID(uuid_type:bool):
        """
        Args:
            uuid_type (bool): True or False

        Returns:
            str: uuid
        """
        generated_uuid = str(uuid.uuid4())
        if uuid_type:
            return generated_uuid
        else:
            return generated_uuid.replace("-", "")

    @staticmethod
    def get_seed(*args):
        """containing only hexadecimal digits. This may be used to exchange the value safely in email or other non-binary environments..

        Args:
            *args: Variable length argument list

        Returns:
            str: hashlib.hexdigest()

        """

        m = hashlib.md5()
        m.update(b"".join([arg.encode("utf-8") for arg in args]))
        return m.hexdigest()

    @staticmethod
    def generate_device_id(seed):
        """
        Args:
            seed: hashlib for device id

        Returns:
             str: "android-" + hashlib.hexdigest()[:16]
        """
        volatile_seed = "12345"
        m = hashlib.md5()
        m.update(seed.encode("utf-8") + volatile_seed.encode("utf-8"))
        return "android-" + m.hexdigest()[:16]

    def generate_signature(self, data):
        """
        Args:
            data: request Method Post data

        Returns:
            str: signed_body={signed_body}.{data}&ig_sig_key_version={ig_sig_key_version}

        """
        body = (
            hmac.new(
                self.config.ig_sig_key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
            ).hexdigest()
            + "."
            + urllib.parse.quote(data)
        )
        signature = "signed_body={body}&ig_sig_key_version={sig_key}"

        return signature.format(sig_key= self.config.sig_key_version, body=body)

    def generate_all_uuids(self):
        """

        Returns
            dict: uuids

        """
        phone_id = self.generate_UUID(uuid_type=True)
        uuid = self.generate_UUID(uuid_type=True)
        client_session_id = self.generate_UUID(uuid_type=True)
        advertising_id = self.generate_UUID(uuid_type=True)
        device_id = self.generate_device_id(self.get_seed(self.raw_account.username, self.raw_account.password))
        uuids = {

                    "phone_id": phone_id,
                    "uuid": uuid,
                    "client_session_id": client_session_id,
                    "advertising_id": advertising_id,
                    "device_id": device_id
        }
        return uuids


    def login(self):
        """login trial using fake device information. This may be used to get real instagram account session and cookie data

        Returns:
            def: send_request

        Examples:
            this example shows how to use function: login

            >>>
            from login import AccountBuilder
            account_builder = AccountBuilder()
            account_builder.login()
        """

        self.logger.info(f"login_trial")
        data = json.dumps({
            "jazoest": "22264",
            "country_codes": '[{"country_code":"1","source":["default"]}]',
            "phone_id": self.uuids["phone_id"],
            "_csrftoken": self.csrftoken,
            "username": self.username,
            "adid": "",
            "guid": self.uuids["uuid"],
            "device_id": self.uuids["device_id"],
            "google_tokens": "[]",
            "password": self.raw_account.password,
            # "enc_password:" "#PWD_INSTAGRAM:4:TIME:ENCRYPTED_PASSWORD"
            "login_attempt_count": "0",
        })

        return self.send_request(f"{self.config.api_url}accounts/login/", post=data, with_signature=True)

    def send_request(self, url, post=None, with_signature=None, extra_sig=None, timeout=30):
        """Request trial . This may be used to get real instagram account session and cookie data

        Args:
            url (str): Description of `url`.
            post (:obj:`str`, optional): required data when you call POST method.
            with_signature (:obj:`bool`, optional): if with_signature, send_request excute generate_signature.
            extra_sig (:obj:`bool`, optional): if extra_sig, send_request add this to post with "&".
            timeout (:obj:`int`, optional): set request timeout
        Returns:
            def: send_request

        Examples:
            this example shows how to use function: login

            >>>
            from login import AccountBuilder
            account_builder = AccountBuilder()
            account_builder.login()
        """
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

#
# account_builder = AccountBuilder(username="toliklazarevNNN95762")
# account_builder.login()

# account_builder = AccoutBuilder(username = "send_direct_items")
# config = ConfigManager()
# account_builder.config = config
# print(account_builder.config.to_dict())
# s = account_builder.generate_signature(data="test")
# print(s)
# #
# #
# config = ConfigManager()
#
# account_builder.config = config
# print(account_builder.config.ig_sig_key)
    # @property
    # def header(self):
    #     self.session.headers.update(self.get_default_header())
    #     self.device.load({})
    #     self.session.headers.update({"User-Agent": self.device.user_agent})
    #

