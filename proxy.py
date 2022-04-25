from model import Proxy

class ProxyManager:
    def __init__(self):
        """this class makes proxy available for all circumstances.

            If the class has public attributes, they may be documented here
            in an ``Attributes`` section and follow the same formatting as a
            function's ``Args`` section. Alternatively, attributes may be documented
            inline with the attribute's declaration (see __init__ method below).

            """

        self._reset()

    def _reset(self):
        """this function makes attributes None.
        """
        self.username = None
        self.password = None
        self.host = None
        self.port = None
        self.status = None

    def _set_variables(self):
        """set proxy's attributes.
        """
        self.username = self._proxy.username if self._proxy else None
        self.password = self._proxy.password if self._proxy else None
        self.host = self._proxy.host if self._proxy else None
        self.port = self._proxy.port if self._proxy else None
        self.status = self._proxy.status if self._proxy else None


    def load(self, query):
        """load model.Proxy using query.
        get available proxy

        Args:
            query (dict): Description of `query`.
        """
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
        """update proxy status.
        get available proxy

        Args:
            **kwargs: Arbitrary keyword arguments.
        """
        self._proxy.update(kwargs)

#
#
# # if __name__ == '__main__' :
# #     '''
# #     test
# #     '''
# #     proxy = ProxySetter()
# #     proxy.load({})
# #     print(proxy.username)


