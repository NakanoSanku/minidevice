import time
import cv2
import scrcpy
from minidevice.screencap import ScreenCap


class ScrcpyCap(ScreenCap):
    def __init__(self, device: scrcpy.Client) -> None:
        """
        __init__ ScrcpyCap

        Args:
            device: scrcpy.Client

        """
        self.client = device
        if not self.client.alive:
            self.client.start(daemon_threaded=True)
            time.sleep(2)

    def screencap_raw(self) -> bytes:
        _, img_data = cv2.imencode(".png", self.screencap_opencv())
        return img_data.tobytes()

    def screencap_opencv(self):
        return self.client.last_frame
    
