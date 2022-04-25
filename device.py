from model import Device

class DeviceManager:
    def __init__(self):
        """this class makes device available for all circumstances.

            If the class has public attributes, they may be documented here
            in an ``Attributes`` section and follow the same formatting as a
            function's ``Args`` section. Alternatively, attributes may be documented
            inline with the attribute's declaration (see __init__ method below).

            """
        self._reset()

    def _reset(self):
        """this function makes attributes None.
        """
        self.app_version = None
        self.android_version = None
        self.android_release = None
        self.dpi = None
        self.resolution = None
        self.manufacturer = None
        self.model = None
        self.cpu = None
        self.version_code = None
        self.user_agent = None

    def _set_variables(self):
        """set device's attributes.
        """
        self.app_version = self._device.app_version
        self.android_version = self._device.android_version
        self.android_release = self._device.android_release
        self.dpi = self._device.dpi
        self.resolution = self._device.resolution
        self.manufacturer = self._device.manufacturer
        self.model = self._device.model
        self.cpu = self._device.cpu
        self.version_code = self._device.version_code
        self.user_agent = self._device.user_agent

    def load(self, query):
        """load model.Device using query.
        load device information

        Args:
            query (dict): Description of `query`.
        """
        self._device = Device.objects(**query).first()
        self._set_variables()

    def to_dict(self) -> dict:
        """make model.Device Object to dictionary .
        """
        del self.__dict__["_device"]
        return self.__dict__




