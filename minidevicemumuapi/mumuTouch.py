import ctypes
import time
from minidevice import Touch

from minidevicemumuapi.mumuapi import MuMuApi
from minidevicemumuapi.config import MUMU_API_DLL_PATH

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
        self.dllPath = emulatorInstallPath + \
            MUMU_API_DLL_PATH if dllPath is None else dllPath
        self.nemu = MuMuApi(self.dllPath)
        # 连接模拟器
        self.handle = self.nemu.connect(
            self.emulatorInstallPath, self.instanceIndex)
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
