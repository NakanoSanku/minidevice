import os
import subprocess

import requests

from minidevice.adb import ADB, ADB_PATH
from minidevice.screencap import ScreenCap

WORK_DIR = os.path.dirname(__file__)
APK_PATH = "{}/bin/DroidCast-debug-1.1.0.apk".format(WORK_DIR)
APK_ANDROID_PATH = "/data/local/tmp/DroidCast-debug-1.0.apk"

class DroidCast(ScreenCap):
    def __init__(self, device, DroidCastServerPort=53516) -> None:
        self.droidcast_adb = ADB(device)
        self.DroidCastServerPort = DroidCastServerPort
        self.class_path = APK_ANDROID_PATH 
        self.DroidCastSession = requests.Session()
        self.__install()
        self.__start()

    def __install(self):
        self.droidcast_adb.push_file(APK_PATH, self.class_path)
        self.droidcast_adb.install_apk(APK_PATH)

    def __start_droidcast(self):
        out = str(
            self.droidcast_adb.adb_command(
                ["shell", "pm", "path", "com.rayworks.droidcast"]
            )
        )
        prefix = "package:"
        postfix = ".apk"
        beg = out.index(prefix, 0)
        end = out.rfind(postfix)

        self.class_path = (
            "CLASSPATH=" + out[beg + len(prefix) : (end + len(postfix))].strip()
        )
        print(self.class_path)
        start_droidcast_cmd = (
            "exec app_process / com.rayworks.droidcast.Main --port={}".format(
                self.DroidCastServerPort
            )
        )
        self.droidcast_popen = subprocess.Popen(
            [
                ADB_PATH,
                "-s",
                self.droidcast_adb.device,
                "shell",
                self.class_path,
                start_droidcast_cmd,
            ],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )

    def __forward_port(self):
        self.droidcast_port = self.droidcast_adb.forward_port(
            "tcp:{}".format(self.DroidCastServerPort)
        )
        self.droidcast_url = "http://localhost:{}/screenshot".format(
            self.droidcast_port
        )
        print(self.droidcast_adb.list_forward_port())
        print(self.droidcast_url)

    def __start(self):
        self.__start_droidcast()
        self.__forward_port()
        print("DroidCast启动完成")

    def __stop(self):
        self.droidcast_adb.remove_forward(self.droidcast_port)  # 清理转发端口
        if self.droidcast_popen.poll() is None:
            self.droidcast_popen.kill()  # 关闭管道

    def screencap_raw(self) -> bytes:
        if self.droidcast_popen.poll() is not None:
            self.__stop()
            self.__start()
        return self.DroidCastSession.get(self.droidcast_url, timeout=3).content

