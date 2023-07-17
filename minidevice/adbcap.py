from adbutils import adb, adb_path
from minidevice.screencap import ScreenCap
import subprocess


class ADBcap(ScreenCap):
    def __init__(self, serial) -> None:
        """
        __init__ ADB 截图方式

        Args:
            serial (str): 设备id
        """
        self.adb = adb.device(serial)

    def screencap_raw(self) -> bytes:
        adb_command = [adb_path(), "-s", self.adb.serial, "exec-out", "screencap", "-p"]
        process = subprocess.Popen(
            adb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        data, err = process.communicate(timeout=10)
        
        if process.returncode == 0:
            return data
