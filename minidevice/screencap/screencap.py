from abc import ABC, abstractmethod


class ScreenCap(ABC):

    @abstractmethod
    def screencap_raw(self) -> bytes:
        """截图源数据"""

    def save_screencap(self, filename="screencap.png"):
        """
        save_screencap 保存截图

        Args:
            filename (str, optional): 截图保存路径. Defaults to "screencap.png".
        """
        with open(filename, "wb") as fp:
            fp.write(self.screencap_raw())
