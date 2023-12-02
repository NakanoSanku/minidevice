import os

from adbutils import adb
from pyminitouch import MNTDevice

from minidevice import Touch

WORK_DIR = os.path.dirname(__file__)
MINITOUCH_PATH = "{}/bin/minitouch/libs".format(WORK_DIR)


class Minitouch(Touch, MNTDevice):
    def __init__(self, serial):
        """
        __init__ minitouch点击方式

        Args:
            device (str): 设备id
        """
        self.__adb = adb.device(serial)
        self.__get_device_info()
        self.__minitouch_install()
        self.__kill_minitouch()
        MNTDevice.__init__(self, serial)
        
    def __kill_minitouch(self):
        pid = self.__adb.shell(['pidof', 'minitouch']).strip()
        if pid:
            self.__adb.shell(['kill', pid])
    

    def __get_device_info(self):
        self.__abi = self.__adb.getprop("ro.product.cpu.abi")

    def __minitouch_install(self):
        MNT_HOME = "/data/local/tmp/minitouch"
        self.__adb.sync.push(f"{MINITOUCH_PATH}/{self.__abi}/minitouch", MNT_HOME)
        self.__adb.shell(f"chmod +x {MNT_HOME}")

    def click(self, x: int, y: int, duration: int = 100):
        MNTDevice.tap(self, [(x, y)], duration=duration)

    def swipe(self, points: list, duration: int = 300):
        MNTDevice.swipe(self, points, duration=duration/(len(points)-1))

    def __del__(self):
        MNTDevice.stop(self)
