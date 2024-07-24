import subprocess

import requests
from adbutils import adb

from minidevice.config import DROIDCAST_APK_ANDROID_PATH, DROIDCAST_APK_PATH, DROIDCAST_APK_VERSION, ADB_EXECUTOR, DROIDCAST_PORT, DROIDCAST_APK_PACKAGE_NAME, DROIDCAST_PM_PATH_SHELL, DROIDCAST_START_CMD
from minidevice.screencap.screencap import ScreenCap
from minidevice.utils.logger import logger


class DroidCast(ScreenCap):
    def __init__(self, serial, display_id: int = None, format: str = "jpeg") -> None:
        """
        __init__ DroidCast截图方法

        Args:
            serial (str): 设备id
            display_id (int): 显示器id use `adb shell dumpsys SurfaceFlinger --display-id` to get
            format (str): 截图编码格式
        """
        self.__adb = adb.device(serial)
        self.__class_path = DROIDCAST_APK_ANDROID_PATH
        self.__display_id = display_id
        self.__droidcast_session = requests.Session()
        self.__droidcast_format = format
        self.__install()
        self.__start()

    def __install(self):
        if DROIDCAST_APK_PACKAGE_NAME not in self.__adb.list_packages():
            self.__adb.install(DROIDCAST_APK_PATH, nolaunch=True)
        else:
            if self.__adb.package_info(DROIDCAST_APK_PACKAGE_NAME)['version_name'] != DROIDCAST_APK_VERSION:
                self.__adb.uninstall(DROIDCAST_APK_PACKAGE_NAME)
                self.__adb.install(DROIDCAST_APK_PATH, nolaunch=True)

    def __start_droidcast(self):
        out = self.__adb.shell(DROIDCAST_PM_PATH_SHELL)
        self.__class_path = "CLASSPATH=" + out.split(":")[1]
        start_droidcast_cmd = DROIDCAST_START_CMD
        adb_command = [ADB_EXECUTOR, "-s", self.__adb.serial,
                       "shell", self.__class_path, start_droidcast_cmd]
        if self.__display_id:
            adb_command.extend(["--display_id={}".format(self.__display_id)])
        logger.info(adb_command)
        self.__droidcast_popen = subprocess.Popen(
            adb_command,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )

    def __forward_port(self):
        self.__droidcast_port = self.__adb.forward_port(DROIDCAST_PORT)
        self.__droidcast_url = f"http://localhost:{self.__droidcast_port}/screenshot?format={self.__droidcast_format}"

    def __start(self):
        self.__start_droidcast()
        self.__forward_port()
        self.screencap_raw()
        logger.info("DroidCast启动完成")

    def __stop(self):
        if self.__droidcast_popen.poll() is None:
            self.__droidcast_popen.kill()  # 关闭管道

    def screencap_raw(self) -> bytes:
        try:
            return self.__droidcast_session.get(self.__droidcast_url, timeout=3).content
        except requests.exceptions.ConnectionError:
            self.__stop()
            self.__start()
            return self.screencap_raw()

    def __del__(self):
        self.__stop()

    def __str__(self) -> str:
        return "DroidCast-url:{}".format(self.__droidcast_url)
