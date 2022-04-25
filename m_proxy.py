import random
from exceptions import NoAccountError
from model import Proxy

class ProxySetter:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.username = None
        self.password = None
        self.host = None
        self.port = None
        self.status = None

    def _set_variables(self):
        self.username = self._proxy.username if self._proxy else None
        self.password = self._proxy.password if self._proxy else None
        self.host = self._proxy.host if self._proxy else None
        self.port = self._proxy.port if self._proxy else None
        self.status = self._proxy.status if self._proxy else None


    def load(self, query):
        self._proxy= Proxy.objects(**query).first()
        self._proxy.status = 'available'
        self._proxy.update(status='available')
        self._set_variables()

    def release_error(self):
        self._proxy.update(status='unavailable')
        self._reset()

    def release(self):
        self._proxy.update(status='available')
        self._reset()

    def update(self, **kwargs):
        self._proxy.update(kwargs)



# if __name__ == '__main__' :
#     '''
#     test
#     '''
#     proxy = ProxySetter()
#     proxy.load({})
#     print(proxy.username)


