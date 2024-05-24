import time
import cv2
import numpy as np
from minidevice import ScreenCap, Touch
import ctypes

DLL_PATH = "/shell/sdk/external_renderer_ipc.dll"


class MuMuApi:
    def __init__(self, dllPath):
        self.nemu = ctypes.CDLL(dllPath)
        # 定义返回类型和参数类型
        self.nemu.nemu_connect.restype = ctypes.c_int
        self.nemu.nemu_connect.argtypes = [ctypes.c_wchar_p, ctypes.c_int]

        self.nemu.nemu_disconnect.argtypes = [ctypes.c_int]

        self.nemu.nemu_capture_display.restype = ctypes.c_int
        self.nemu.nemu_capture_display.argtypes = [
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_ubyte),
        ]

        self.nemu.nemu_input_text.restype = ctypes.c_int
        self.nemu.nemu_input_text.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_char_p,
        ]

        self.nemu.nemu_input_event_touch_down.restype = ctypes.c_int
        self.nemu.nemu_input_event_touch_down.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]

        self.nemu.nemu_input_event_touch_up.restype = ctypes.c_int
        self.nemu.nemu_input_event_touch_up.argtypes = [ctypes.c_int, ctypes.c_int]

        self.nemu.nemu_input_event_key_down.restype = ctypes.c_int
        self.nemu.nemu_input_event_key_down.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]

        self.nemu.nemu_input_event_key_up.restype = ctypes.c_int
        self.nemu.nemu_input_event_key_up.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]

    def connect(self, emulatorInstallPath, instanceIndex):
        return self.nemu.nemu_connect(emulatorInstallPath, instanceIndex)

    def disconnect(self, handle):
        return self.nemu.nemu_disconnect(handle)

    def captureDisplay(self, handle, displayId, bufferSize, width, height, pixels):
        return self.nemu.nemu_capture_display(
            handle, displayId, bufferSize, width, height, pixels
        )

    def inputText(self, handle, size, buf):
        return self.nemu.nemu_input_text(handle, size, buf)

    def inputEventTouchDown(self, handle, displayId, xPoint, yPoint):
        return self.nemu.nemu_input_event_touch_down(handle, displayId, xPoint, yPoint)

    def inputEventTouchUp(self, handle, displayId):
        return self.nemu.nemu_input_event_touch_up(handle, displayId)

    def inputEventKeyDown(self, handle, displayId, keyCode):
        return self.nemu.nemu_input_event_key_down(handle, displayId, keyCode)

    def inputEventKeyUp(self, handle, displayId, keyCode):
        return self.nemu.nemu_input_event_key_up(handle, displayId, keyCode)


class MuMuScreenCap(ScreenCap):
    def __init__(
        self,
        instanceIndex,
        emulatorInstallPath: str,
        dllPath: str = None,
        displayId: int = 0,
    ):
        """
        __init__ MumuApi 截图

        基于/shell/sdk/external_renderer_ipc.dll实现截图mumu模拟器

        Args:
            instanceIndex (int): 模拟器实例的编号
            emulatorInstallPath (str): 模拟器安装路径
            dllPath (str, optional): dll文件存放路径，一般会根据模拟器路径获取. Defaults to None.
            displayId (int, optional): 显示窗口id，一般无需填写. Defaults to 0.
        """
        self.displayId = displayId
        self.instanceIndex = instanceIndex
        self.emulatorInstallPath = emulatorInstallPath
        self.dllPath = emulatorInstallPath + DLL_PATH if dllPath is None else dllPath
        self.nemu = MuMuApi(self.dllPath)
        # 连接模拟器
        self.handle = self.nemu.connect(self.emulatorInstallPath, self.instanceIndex)
        self.__getDisplayInfo()

    def __getDisplayInfo(self):
        self.width = ctypes.c_int(0)
        self.height = ctypes.c_int(0)
        result = self.nemu.captureDisplay(
            self.handle,
            self.displayId,
            0,
            ctypes.byref(self.width),
            ctypes.byref(self.height),
            None,
        )
        if result != 0:
            print("Failed to get the display size.")
            return None
        # 根据宽度和高度计算缓冲区大小
        self.bufferSize = self.width.value * self.height.value * 4
        # 创建一个足够大的缓冲区来存储像素数据
        self.pixels = (ctypes.c_ubyte * self.bufferSize)()
        print(
            self.handle,
            self.displayId,
            self.bufferSize,
            self.width,
            self.height,
            self.pixels,
        )

    def screencap_raw(self) -> bytes:
        self.width = ctypes.c_int(self.width.value)
        self.height = ctypes.c_int(self.height.value)
        result = self.nemu.captureDisplay(
            self.handle,
            self.displayId,
            self.bufferSize,
            self.width,
            self.height,
            self.pixels,
        )
        if result > 1:
            raise BufferError("截图错误")
        inverted_image = np.flipud(
            cv2.cvtColor(
                np.ctypeslib.as_array(self.pixels).reshape(
                    (self.height.value, self.width.value, 4)
                ),
                cv2.COLOR_RGBA2BGR,
            )
        )
        _, buffer = cv2.imencode(".jpg", inverted_image)  # 编码为JPEG格式
        # 转换为bytes
        return buffer.tobytes()

    def __del__(self):
        self.nemu.disconnect(self.handle)


class MuMuTouch(Touch):
    def __init__(
        self,
        instanceIndex,
        emulatorInstallPath: str,
        dllPath: str = None,
        displayId: int = 0,
    ):
        """
        __init__ MumuApi 操作

        基于/shell/sdk/external_renderer_ipc.dll实现操作mumu模拟器

        Args:
            instanceIndex (int): 模拟器实例的编号
            emulatorInstallPath (str): 模拟器安装路径
            dllPath (str, optional): dll文件存放路径，一般会根据模拟器路径获取. Defaults to None.
            displayId (int, optional): 显示窗口id，一般无需填写. Defaults to 0.
        """
        self.displayId = displayId
        self.instanceIndex = instanceIndex
        self.emulatorInstallPath = emulatorInstallPath
        self.dllPath = emulatorInstallPath + DLL_PATH if dllPath is None else dllPath
        self.nemu = MuMuApi(self.dllPath)
        # 连接模拟器
        self.handle = self.nemu.connect(self.emulatorInstallPath, self.instanceIndex)
        self.__getDisplayInfo()

    def __getDisplayInfo(self):
        self.width = ctypes.c_int(0)
        self.height = ctypes.c_int(0)
        result = self.nemu.captureDisplay(
            self.handle,
            self.displayId,
            0,
            ctypes.byref(self.width),
            ctypes.byref(self.height),
            None,
        )
        if result != 0:
            print("Failed to get the display size.")
            return None

    def click(self, x: int, y: int, duration: int = 100):
        x, y = self.xyChange(x, y)
        self.nemu.inputEventTouchDown(self.handle, self.displayId, x, y)
        time.sleep(duration / 1000)
        self.nemu.inputEventTouchUp(self.handle, self.displayId)

    def swipe(self, points: list, duration: int = 300):
        for point in points:
            x, y = self.xyChange(point[0], point[1])
            self.nemu.inputEventTouchDown(self.handle, self.displayId, x, y)
            time.sleep(duration / len(points) / 1000)
        self.nemu.inputEventTouchUp(self.handle, self.displayId)

    def xyChange(self, x, y):
        x, y = int(x), int(y)
        x, y = self.height.value - y, x
        return x, y

    def __del__(self):
        self.nemu.disconnect(self.handle)


if __name__ == "__main__":
    test = MuMuScreenCap(0, "D:\\MuMuPlayer-12.0")
    # for i in range(5):
    #     s = time.time()
    #     image = test.screencap_raw()
    #     print((time.time() - s) * 1000)
    #     cv2.imshow("{}".format(i), image)
    #     cv2.waitKey()
    # for i in range(10):
    #     s = time.time()
    #     test.screencap_raw()
    #     print((time.time() - s) * 1000)
    test.save_screencap()
