import threading
from minidevice import MaaTouch
from minidevice.screencap.screencap import ScreenCap
from minidevice.touch.touch import Touch
from minidevice.utils.logger import logger


class MiniDevice:
    def __init__(self, serial=None, screenshot_method=None, touch_method=None, screenshot_timeout=15):
        """设备操作类

        Args:
            serial (str): 设备id 或者 其他初始化设备标识比如句柄
            screenshot_method (CAP_METHOD, optional): ScreenCap. Defaults to None.
            touch_method (TOUCH_METHOD, optional): Touch. Defaults to None.
            screenshot_timeout (int, optional): 截图延迟，每张截图之间的延迟时间(包含截图过程) 单位ms. Defaults to 500.
        """
        self.__serial = serial
        self.__cap_method = None
        self.__touch_method = None

        if screenshot_method:
            self.__cap_method = self._initialize_method(screenshot_method, ScreenCap)
        if touch_method:
            self.__touch_method = self._initialize_method(touch_method, Touch)

        self.__touch_thread_lock = threading.Lock()
        self.__screenshot_thread_lock = threading.Lock()
        self.__screenshot_timeout_timer = None
        self.__screenshot_timeout = screenshot_timeout / 1000
        self.__current_screenshot = None

    def _initialize_method(self, method, super_class):
        if isinstance(method, super_class):
            return method
        if isinstance(method, type) and issubclass(method, super_class):
            if self.__serial:
                return method(self.__serial)
            raise TypeError(f"{method.__name__} missing instantiation parameter")
        raise TypeError(f"{method.__name__} is not a subclass of {super_class.__name__}")

    def __timeout_fun(self):
        """仅用于延迟定时器"""
        pass

    def screenshot_raw(self) -> bytes:
        """截图"""
        if self.__cap_method:
            if not self.__screenshot_timeout_timer or not self.__screenshot_timeout_timer.is_alive():
                with self.__screenshot_thread_lock:
                    self.__screenshot_timeout_timer = threading.Timer(
                        self.__screenshot_timeout, self.__timeout_fun
                    )
                    self.__screenshot_timeout_timer.start()
                    self.__current_screenshot = self.__cap_method.screencap_raw()
                    logger.debug(f"take screenshot on {self.__serial}")
        return self.__current_screenshot

    def save_screenshot(self, path: str = "screenshot.png") -> None:
        """保存截图"""
        with open(path, 'wb') as file:
            file.write(self.screenshot_raw())

    def _perform_touch_action(self, action, *args, duration=300):
        """执行触摸动作的私有方法，减少代码冗余"""
        try:
            if duration <= 0:
                raise ValueError("Duration must be greater than 0")

            with self.__touch_thread_lock:
                # 调用触摸方法执行动作
                getattr(self.__touch_method, action)(*args, duration)
                logger.debug(f"{action}d {self.__serial} at coordinates {args}")

        except Exception as e:
            logger.error(f"Error during {action}: {e}")

    def click(self, x: int, y: int, duration: int = 100):
        """点击"""
        self._perform_touch_action('click', x, y, duration=duration)

    def swipe(self, points: list, duration: int = 300):
        """滑动"""
        self._perform_touch_action('swipe', points, duration=duration)
