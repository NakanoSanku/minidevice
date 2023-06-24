import os

from minidevice.adb import ADB
from pyminitouch import MNTDevice
from minidevice.logger import logger
from minidevice.touch import Touch

WORK_DIR = os.path.dirname(__file__)
MINITOUCH_PATH = "{}/bin/minitouch/libs".format(WORK_DIR)


class Minitouch(Touch, MNTDevice):
    def __init__(self, device):
        """
        __init__ minitouch点击方式

        Args:
            device (str): 设备id
        """
        self.minitouch_adb = ADB(device)
        self.__get_device_info()
        self.__minitouch_install()
        MNTDevice.__init__(self, device)

    def __get_device_info(self):
        self.abi = self.minitouch_adb.get_abi()

    def __minitouch_install(self):
        MNT_HOME = "/data/local/tmp/minitouch"
        self.minitouch_adb.push_file(f"{MINITOUCH_PATH}/{self.abi}/minitouch", MNT_HOME)
        self.minitouch_adb.change_file_permission("+x", MNT_HOME)

    def click(self, x: int, y: int, duration: int = 100):
        MNTDevice.tap(self, [(x, y)], duration=duration)
        logger.debug(f"minitouch click ({x},{y}) consume:{duration}ms")

    def swipe(self, points: list, duration: int = 300):
        MNTDevice.swipe(self, points, duration=duration)
        logger.debug(
            f"minitouch swipe from ({points[0]}) to ({points[-1]}) consume:{duration}ms"
        )

    def __del__(self):
        MNTDevice.stop(self)

if __name__ == "__main__":
    a = Minitouch("127.0.0.1:16384")
    a.stop()
