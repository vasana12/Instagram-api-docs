from model import RawAccount

class RawAccountManager:
    def __init__(self):
        """this class makes RawAccount available for all circumstances.

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
        self.status = None

    def _set_variables(self):
        """set proxy's attributes.
        """
        self.username = self._raw_account.username
        self.password = self._raw_account.password
        self.status = self._raw_account.status

    def load(self, query):
        ### 1. device 셋팅을 위해 raw_account 계정 가져오기
        """load model.RawAccount using query.
        Get raw_account account for device setting

         Args:
             query (dict): status : setting_before.
         """
        query.update(status="setting_before")
        self._raw_account = RawAccount.objects(**query).first()
        self._set_variables()

    def update(self, **kwargs):
        """update raw_account status.

         Args:
             **kwargs: Arbitrary keyword arguments.
         """
        self._raw_account.update(kwargs)

#
# if __name__ == '__main__' :
#     """
#     test device
#     """
#     raw_account = RawAccountSetter()
#     raw_account.load({})
#     print(raw_account)





