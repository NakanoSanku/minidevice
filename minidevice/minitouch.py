import os

from adbutils import adb
from pyminitouch import MNTDevice

from minidevice.touch import Touch

WORK_DIR = os.path.dirname(__file__)
MINITOUCH_PATH = "{}/bin/minitouch/libs".format(WORK_DIR)


class Minitouch(Touch, MNTDevice):
    def __init__(self, serial):
        """
        __init__ minitouch点击方式

        Args:
            device (str): 设备id
        """
        self.adb = adb.device(serial)
        self.__get_device_info()
        self.__minitouch_install()
        MNTDevice.__init__(self, serial)

    def __get_device_info(self):
        self.abi = self.adb.getprop("ro.product.cpu.abi")

    def __minitouch_install(self):
        MNT_HOME = "/data/local/tmp/minitouch"
        self.adb.sync.push(f"{MINITOUCH_PATH}/{self.abi}/minitouch", MNT_HOME)
        self.adb.shell(f"chmod +x {MNT_HOME}")

    def click(self, x: int, y: int, duration: int = 100):
        MNTDevice.tap(self, [(x, y)], duration=duration)

    def swipe(self, points: list, duration: int = 300):
        MNTDevice.swipe(self, points, duration=duration/(len(points)-1))

    def __del__(self):
        MNTDevice.stop(self)
