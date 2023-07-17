import os
import subprocess

import requests
from adbutils import adb, adb_path

from minidevice.screencap import ScreenCap

WORK_DIR = os.path.dirname(__file__)
APK_PATH = "{}/bin/DroidCast-debug-1.1.0.apk".format(WORK_DIR)
APK_ANDROID_PATH = "/data/local/tmp/DroidCast-debug-1.0.apk"


class DroidCast(ScreenCap):
    def __init__(self, device) -> None:
        """
        __init__ DroidCast截图方法

        Args:
            device (str): 设备id

        """
        self.adb = adb.device(device)
        self.class_path = APK_ANDROID_PATH
        self.DroidCastSession = requests.Session()
        self.__install()
        self.__start()

    def __install(self):
        if "com.rayworks.droidcast" not in self.adb.list_packages():
            self.adb.install(APK_PATH, nolaunch=True)

    def __start_droidcast(self):
        out = self.adb.shell("pm path com.rayworks.droidcast")
        self.class_path = "CLASSPATH=" + out.split(":")[1]
        start_droidcast_cmd = "exec app_process / com.rayworks.droidcast.Main"
        self.droidcast_popen = subprocess.Popen(
            [
                adb_path(),
                "-s",
                self.adb.serial,
                "shell",
                self.class_path,
                start_droidcast_cmd,
            ],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )

    def __forward_port(self):
        self.droidcast_port = self.adb.forward_port(53516)
        self.droidcast_url = f"http://localhost:{self.droidcast_port}/screenshot"

    def __start(self):
        self.__start_droidcast()
        self.__forward_port()
        self.screencap_raw()
        print("DroidCast启动完成")

    def __stop(self):
        if self.droidcast_popen.poll() is None:
            self.droidcast_popen.kill()  # 关闭管道

    def screencap_raw(self) -> bytes:
        if self.droidcast_popen.poll() is not None:
            self.__stop()
            self.__start()
        return self.DroidCastSession.get(self.droidcast_url, timeout=3).content

    def __del__(self):
        self.__stop()

    def __str__(self) -> str:
        return "DroidCast-url:{}".format(self.droidcast_url)
