import random
import logging
from exceptions import NoAccountError
from model import Config

class ConfigSetter:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.sig_key_version = None
        self.ig_sig_key = None
        self.api_domain = None
        self.api_url = None

    def _set_variables(self):
        self.sig_key_version = self._config.sig_key_version if self._config else None
        self.ig_sig_key = self._config.ig_sig_key if self._config else None
        self.api_domain = self._config.api_domain if self._config else None
        self.api_url = self._config.api_url if self._config else None

    def load(self, query):
        self._config = Config.objects(**query).first()
        self._set_variables()

    def to_dict(self):
        del self.__dict__["_config"]
        return self.__dict__


