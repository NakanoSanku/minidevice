from minidevice.adb import ADB
from minidevice.logger import logger
from minidevice.touch import Touch


class ADBtouch(Touch, ADB):
    def __init__(self, device) -> None:
        """
        __init__ ADB 操作方式

        Args:
            device (str): 设备id
        """
        ADB.__init__(self, device=device)

    def click(self, x: int, y: int, duration: int = 100):
        ADB.click(self, x, y, duration)
        logger.debug(f"ADB click ({x},{y}) consume:{duration}ms")

    def swipe(self, points: list, duration: int = 300):
        start_x, start_y = points[0]
        end_x, end_y = points[-1]
        ADB.swipe(self, start_x, start_y, end_x, end_y, duration)
        logger.debug(
            f"ADB swipe from ({points[0]}) to ({points[-1]}) consume:{duration}ms"
        )
