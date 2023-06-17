import os
import subprocess

import requests

from minidevice.adb import ADB, ADB_PATH
from minidevice.screencap import ScreenCap

WORK_DIR = os.path.dirname(__file__)
APK_PATH = "{}/bin/DroidCast-debug-1.1.0.apk".format(WORK_DIR)
APK_ANDROID_PATH = "/data/local/tmp/DroidCast-debug-1.0.apk"

class DriodCast(ScreenCap):
    def __init__(self, device, DriodCastServerPort=53516) -> None:
        self.driodcast_adb = ADB(device)
        self.DriodCastServerPort = DriodCastServerPort
        self.class_path = APK_ANDROID_PATH 
        self.DriodCastSession = requests.Session()
        self._install()
        self._start()

    def _install(self):
        self.driodcast_adb.push_file(APK_PATH, self.class_path)
        self.driodcast_adb.install_apk(APK_PATH)

    def _start_driodcast(self):
        out = str(
            self.driodcast_adb.adb_command(
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
        start_driodcast_cmd = (
            "exec app_process / com.rayworks.droidcast.Main --port={}".format(
                self.DriodCastServerPort
            )
        )
        self.driodcast_popen = subprocess.Popen(
            [
                ADB_PATH,
                "-s",
                self.driodcast_adb.device,
                "shell",
                self.class_path,
                start_driodcast_cmd,
            ],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )

    def _forward_port(self):
        self.driodcast_port = self.driodcast_adb.forward_port(
            "tcp:{}".format(self.DriodCastServerPort)
        )
        self.driodcast_url = "http://localhost:{}/screenshot".format(
            self.driodcast_port
        )
        print(self.driodcast_adb.list_forward_port())
        print(self.driodcast_url)

    def _start(self):
        self._start_driodcast()
        self._forward_port()
        print("DriodCast启动完成")

    def _stop(self):
        self.driodcast_adb.remove_forward(self.driodcast_port)  # 清理转发端口
        if self.driodcast_popen.poll() is None:
            self.driodcast_popen.kill()  # 关闭管道

    def screencap_raw(self) -> bytes:
        if self.driodcast_popen.poll() is not None:
            self._stop()
            self._start()
        return self.DriodCastSession.get(self.driodcast_url, timeout=3).content
