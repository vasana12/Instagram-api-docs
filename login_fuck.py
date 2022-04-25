# from datetime import datetime
# import hashlib
# import hmac
# import json
# import random
# import time
# import hashlib
# import uuid
# from typing import Optional
#
# from m_raw_account import RawAccountSetter
#
# try:
#     from json.decoder import JSONDecodeError
# except ImportError:
#     JSONDecodeError = ValueError
# import six.moves.urllib as urllib
import logging
import random
import time

import requests
from m_proxy import ProxySetter
from m_device import DeviceSetter


class AccoutBuilder:

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

    @property
    def proxy(self):
        # """proxy.ProxyManager: set and get proxy
        #
        # Examples:
        #     this example shows how to get and set proxy
        #
        #     >>> ### setter
        #     from proxy import ProxyManager
        #     proxy = ProxyManager()
        #     self.proxy(proxy)
        #
        #     >>> ### getter
        #     self.proxy()
        # """

        return self._proxy

    @proxy.setter
    def proxy(self, proxy: ProxySetter):  # setter
        """proxy.ProxyManager"""
        proxy.load({})
        self._proxy = proxy

        # self._proxy = f"http://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"

    @property
    def device(self):
        """device.DeviceManager: set and get proxy

        Examples:
            this example shows how to get and set proxy

            >>> ### setter
            from device import DeviceManager
            device = DeviceManager()
            self.device(device)

            >>> ### getter
            self.device()
        """
        return self._device

    @device.setter
    def device(self, device:DeviceSetter):
        device.load({})
        self._device = device


    @staticmethod
    def get_default_header():
        """dict: Properties should be documented in their getter method.

        Returns:
            dict: headers.

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

account_builder = AccoutBuilder(username = "send_direct_items")


proxy = ProxySetter()
account_builder.proxy = proxy
print(account_builder.proxy.host)
    # @property
    # def header(self):
    #     self.session.headers.update(self.get_default_header())
    #     self.device.load({})
    #     self.session.headers.update({"User-Agent": self.device.user_agent})
    #
    #
