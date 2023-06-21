from minidevice import (
    DroidCast,
    Minicap,
    Minitouch,
    ADBcap,
    ADBtouch,
)


class MiniDevice:
    SCREEN_CAP_METHODS = {
        "DroidCast": DroidCast,
        "Minicap": Minicap,
        "ADBcap": ADBcap,
    }

    TOUCH_METHODS = {
        "Minitouch": Minitouch,
        "ADBtouch": ADBtouch,
    }

    def __init__(
        self, device, screen_cap_method="DroidCast", touch_method="Minitouch"):
        """
        __init__ MiniDevice
        TOUCH_METHODS = {"Minitouch": Minitouch, "ADBtouch": ADBtouch}
        SCREEN_CAP_METHODS = {"DroidCast": DroidCast, "Minicap": Minicap, "ADBcap": ADBcap}
        Args:
            device (str): 设备id
            screen_cap_method (str, optional): 设备截图方案. Defaults to "DroidCast".
            touch_method (str, optional): 设备点击方案. Defaults to "Minitouch".
        """
        screen_cap_class = self.SCREEN_CAP_METHODS.get(screen_cap_method, DroidCast)
        touch_class = self.TOUCH_METHODS.get(touch_method, Minitouch)
        self.__screen_cap_method = screen_cap_class(device)
        self.__touch_method = touch_class(device)

    def get_screen(self):
        """返回opencv格式截图"""
        return self.__screen_cap_method.screencap_opencv()

    def save_screen(self, filename):
        """保存截图"""
        self.__screen_cap_method.save_screencap(filename)

    def click(self, x: int, y: int, duraiton: int = 100):
        """点击(x,y)点持续duration ms"""
        self.__touch_method.click(x, y, duraiton)

    def swipe(self, points: list, duration: int = 300):
        """按照points轨迹点滑动 持续duration ms"""
        self.__touch_method.swipe(points, duration)
