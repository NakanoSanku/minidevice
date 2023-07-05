from abc import ABC, abstractmethod

import cv2
import numpy as np


class ScreenCap(ABC):
    @abstractmethod
    def screencap_raw(self) -> bytes:
        """截图源数据"""

    def screencap_opencv(self):
        """opencv格式截图"""
        raw = self.screencap_raw()
        return cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)

    def save_screencap(self, filename="screencap.png"):
        """
        save_screencap 保存截图

        Args:
            filename (str, optional): 截图保存路径. Defaults to "screencap.png".
        """
        with open(filename, "wb") as fp:
            fp.write(self.screencap_raw())
