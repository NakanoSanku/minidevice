from minidevice import *
import threading

from minidevice.logger import logger




class MiniDevice:
    def __init__(self, serial: str, capMethod: ADBtouch | Minicap | DroidCast = None,
                 touchMethod: ADBtouch | Minitouch = None, screenshotTimeout=500) -> None:
        """设备操作类

        Args:
            serial (str): 设备id
            capMethod (CAP_METHOD,optional): ADBtouch | Minicap | DroidCast. Defaults to None
            touchMethod (TOUCH_METHOD, optional): ADBtouch | Minitouch. Defaults to None.
            screenshotTimeout (int, optional):截图延迟，每张截图之间的延迟时间(包含截图过程) 单位ms. Defaults to 500.
        """
        self.__serial = serial
        # TypeError: issubclass() arg 1 must be a class
        def typeAndClassCheck(method,superClass):
            if method:
                if isinstance(method,type):
                    if not issubclass(method,superClass):
                        raise TypeError(f"{method.__name__} is not a subclass of {superClass.__name__}")
                else:
                    raise TypeError(f"{capMethod.__name__} is not a class")
        typeAndClassCheck(capMethod,ScreenCap)
        typeAndClassCheck(touchMethod,Touch)
        self.__capMethod = capMethod(serial) if capMethod else None
        self.__touchMethod = touchMethod(serial) if touchMethod else None
        self.__touchThreadLock = None # 操作线程锁
        self.__touchTimeoutTimer = None  # 操作延迟定时器
        self.__screenshotThreadLock = None  # 截图线程锁
        self.__screenshotTimeoutTimer = None  # 截图延迟定时器
        self.__screenshotTimeout = screenshotTimeout / 1000  # 截图延迟
        self.__current_screenshot = None  # 上一张截图

    def __timeoutFun(self):
        """仅用于延迟定时器"""
        pass

    def screenshot(self) -> bytes:
        """截图"""
        if self.__capMethod:
            if not self.__screenshotThreadLock:
                # 创建截图线程锁
                self.__screenshotThreadLock = threading.Lock()
            if (self.__screenshotTimeoutTimer is not None and not self.__screenshotTimeoutTimer.is_alive()) or self.__screenshotTimeoutTimer is None:
                # 获取锁
                self.__screenshotThreadLock.acquire()
                try:
                    self.__screenshotTimeoutTimer = threading.Timer(self.__screenshotTimeout,
                                                                    self.__timeoutFun)
                    self.__screenshotTimeoutTimer.start()
                    self.__current_screenshot = self.__capMethod.screencap_raw()
                    logger.debug(f"take screenshot on {self.__serial}")
                    
                finally:
                    # 释放锁
                    self.__screenshotThreadLock.release()

        return self.__current_screenshot

    def click(self, x: int, y: int, duration: int=100):
        """点击

        Args:
            x (int): x
            y (int): y
            duration (int): 触摸时间 默认100ms
        """

        if self.__touchMethod:
            
            def func():
                self.__touchTimeoutTimer = threading.Timer(duration/1000,self.__timeoutFun)
                self.__touchTimeoutTimer.start()     
                self.__touchMethod.click(x, y, duration) 
                logger.debug(f"clicked {self.__serial} at coordinates ({x}, {y})")
                
            if not self.__touchThreadLock:
                self.__touchThreadLock = threading.Lock()
                
            self.__touchThreadLock.acquire()
            try:    
                if (self.__touchTimeoutTimer is not None and not self.__touchTimeoutTimer.is_alive()) or self.__touchTimeoutTimer is None:
                    func()
                if self.__touchTimeoutTimer and self.__touchTimeoutTimer.is_alive():
                    def waitFunc():
                        self.__touchTimeoutTimer.join()
                        func()
                    threading.Thread(target=waitFunc).start()# 启动一个新线程在上一个操作执行完后执行当前操作

            finally:
                self.__touchThreadLock.release()  
                
                
    def swipe(self, points: list, duration: int=300):
        """滑动

        Args:
            points (list): [(x,y),(x,y)....]
            duration (int): 触摸时间 默认300ms
        """
        if self.__touchMethod:

            def func():
                self.__touchTimeoutTimer = threading.Timer(duration/1000,self.__timeoutFun)
                self.__touchTimeoutTimer.start()     
                self.__touchMethod.swipe(points, duration) 
                logger.debug(f"swiped {self.__serial} from {points[0]} to {points[-1]}")
                
            if not self.__touchThreadLock:
                self.__touchThreadLock = threading.Lock()
                
            self.__touchThreadLock.acquire()
            try:    
                if (self.__touchTimeoutTimer is not None and not self.__touchTimeoutTimer.is_alive()) or self.__touchTimeoutTimer is None:
                    func()
                if self.__touchTimeoutTimer and self.__touchTimeoutTimer.is_alive():
                    def waitFunc():
                        self.__touchTimeoutTimer.join()
                        func()
                    threading.Thread(target=waitFunc).start()# 启动一个新线程在上一个操作执行完后执行当前操作
            finally:
                self.__touchThreadLock.release()  
