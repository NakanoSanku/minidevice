from minidevice import (
    DroidCast,
    Minicap,
    Minitouch,
    ADBcap,
    ADBtouch,
    # ScrcpyCap,
    # ScrcpyTouch,
)
# import scrcpy


class MiniDevice:
    SCREEN_CAP_METHODS = {
        "DroidCast": DroidCast,
        "Minicap": Minicap,
        "ADBcap": ADBcap,
        # "ScrcpyCap": ScrcpyCap,
    }

    TOUCH_METHODS = {
        "Minitouch": Minitouch,
        "ADBtouch": ADBtouch,
        # "ScrcpyTouch": ScrcpyTouch,
    }

    def __init__(
        self, device, screen_cap_method="DroidCast", touch_method="Minitouch", **kwargs
    ):
        """
        __init__ MiniDevice
        TOUCH_METHODS = {"Minitouch": Minitouch, "ADBtouch": ADBtouch}
        SCREEN_CAP_METHODS = {"DroidCast": DroidCast, "Minicap": Minicap, "ADBcap": ADBcap}
        如果点击方法或者截图方法采用scrcpy,强制替换两种方法都为scrcpy
        Args:
            device (str): 设备id
            screen_cap_method (str, optional): 设备截图方案. Defaults to "DroidCast".
            touch_method (str, optional): 设备点击方案. Defaults to "Minitouch".
        """
        screen_cap_class = self.SCREEN_CAP_METHODS.get(screen_cap_method, DroidCast)
        touch_class = self.TOUCH_METHODS.get(touch_method, Minitouch)
        # if screen_cap_method == "ScrcpyCap" or touch_method == "ScrcpyTouch":
        #     screen_cap_class = self.SCREEN_CAP_METHODS.get("ScrcpyCap")
        #     touch_class = self.TOUCH_METHODS.get("ScrcpyTouch")
        #     self.client = scrcpy.Client(device=device, **kwargs)
        #     self.__screen_cap_method = screen_cap_class(self.client)
        #     self.__touch_method = touch_class(self.client)
        # else:
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
