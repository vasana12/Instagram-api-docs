from model import RawAccount

class RawAccountManager:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.username = None
        self.password = None
        self.status = None

    def _set_variables(self):
        self.username = self._raw_account.username
        self.password = self._raw_account.password
        self.status = self._raw_account.status

    def load(self, query):
        ### 1. device 셋팅을 위해 raw_account 계정 가져오기
        query.update(status="setting_before")
        self._raw_account = RawAccount.objects(**query).first()
        self._set_variables()
    def update(self, **kwargs):
        self._raw_account.update(kwargs)

#
# if __name__ == '__main__' :
#     """
#     test device
#     """
#     raw_account = RawAccountSetter()
#     raw_account.load({})
#     print(raw_account)





