from adbutils import adb
from minidevice import Touch


class ADBtouch(Touch):
    def __init__(self, serial) -> None:
        """
        __init__ ADB 操作方式

        Args:
            serial (str): 设备id
        """
        self.__adb = adb.device(serial)

    def click(self, x: int, y: int, duration: int = 100):
        adb_command = ["input", "touchscreen", "swipe"]
        adb_command.extend([str(x), str(y), str(x), str(y), str(duration)])
        self.__adb.shell(adb_command)

    def swipe(self, points: list, duration: int = 300):
        start_x, start_y = points[0]
        end_x, end_y = points[-1]
        self.__adb.swipe(self, start_x, start_y, end_x, end_y, duration/1000)
