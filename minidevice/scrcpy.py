import time
import cv2
import scrcpy
from screencap import ScreenCap
from touch import Touch


class ScrcpyCap(ScreenCap):
    def __init__(self, device: scrcpy.Client) -> None:
        """
        __init__ ScrcpyCap

        Args:
            device: scrcpy.Client

        """
        self.client = device

    def screencap_raw(self) -> bytes:
        """截图源数据"""
        _, img_data = cv2.imencode(".png", self.screencap_opencv())
        return img_data.tobytes()

    def screencap_opencv(self):
        return self.client.last_frame


class ScrcpyTouch(Touch):
    def __init__(self, device: scrcpy.Client) -> None:
        self.client = device

    def click(self, x: int, y: int, duration: int = 100):
        self.client.control.touch(x, y, scrcpy.ACTION_DOWN)
        time.sleep(duration / 1000)
        self.client.control.touch(x, y, scrcpy.ACTION_UP)

    def swipe(self, points: list, duration: int = 300):
        self.client.control.touch(points[0][0], points[0][1], scrcpy.ACTION_DOWN)
        for point in points[1:-1]:
            time.sleep(duration / (len(points) * 1000))
            self.client.control.touch(point[0], point[1], scrcpy.ACTION_MOVE)
        self.client.control.touch(points[-1][0], points[-1][1], scrcpy.ACTION_UP)
