from minidevice import logger
from minidevice.adb import ADB
from minidevice.screencap import ScreenCap

import scrcpy
scrcpy.Client()
class ADBcap(ScreenCap, ADB):
    def __init__(self, device) -> None:
        """
        __init__ ADB 截图方式

        Args:
            device (str): 设备id
        """
        ADB.__init__(self, device=device)

    def screencap_raw(self) -> bytes:
        logger.debug(f"screen by ADB")
        return ADB.__screencap_raw(self)
