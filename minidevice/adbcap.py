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
        self.__adb = adb.device(serial)

    def screencap_raw(self) -> bytes:
        """
        截图并以字节流的形式返回Android设备的屏幕。

        :param serial: 设备的序列号。
        :return: 截图的字节数据。
        """
        try:
            adb_command = [adb_path(), "-s", self.__adb.serial, "exec-out", "screencap", "-p"]
            process = subprocess.Popen(
                adb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            data, err = process.communicate(timeout=10)
            
            if process.returncode == 0 and data:
                return data
            else:
                raise subprocess.TimeoutExpired(
                    None, timeout=10, stdout=data, stderr=err
                )
        except subprocess.TimeoutExpired as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Error while screencapping the device: {e}")