import shutil
import subprocess
import random
from minidevice.logger import logger


from minidevice.screencap import ScreenCap
from minidevice.touch import Touch

ADB_PATH = "adb"
if shutil.which("adb.exe") is None:
    import os

    WORK_DIR = os.path.dirname(__file__)
    ADB_PATH = shutil.which("adb.exe", path="{}/bin".format(WORK_DIR))


class ADB:
    def __init__(self, device=None):
        self.device = device

    def adb_command(self, command: list):
        """执行shell脚本语句,获取返回的源数据"""
        adb_command = [ADB_PATH]
        if self.device:
            adb_command.extend(["-s", self.device])
        adb_command.extend(command)
        try:
            process = subprocess.Popen(
                adb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            data, err = process.communicate(timeout=10)
            if process.returncode == 0:
                return data
            else:
                logger.error("ADB命令执行失败\n报错信息:{}".format(err))
        except FileNotFoundError:
            logger.error("ADB不存在或无法执行")
        except subprocess.TimeoutExpired:
            logger.error("ADB命令执行超时")

    def __run_adb_command(self, command: list):
        adb_command = [ADB_PATH]
        if self.device:
            adb_command.extend(["-s", self.device])
        adb_command.extend(command)
        try:
            result = subprocess.run(adb_command, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("\nADB命令执行失败\n报错信息:{}".format(result.stderr))
            return result.stdout
        except subprocess.CalledProcessError as e:
            # 执行失败，处理异常情况
            logger.error(f"命令执行失败\n返回码:, {e.returncode}\n标准错误:{e.stderr}")
        except subprocess.TimeoutExpired as e:
            # 命令执行超时，处理超时情况
            logger.error("命令执行超时")

    def forward_port(self, server, port=None) -> int:
        while True:
            localport = random.randint(11111, 20000) if port is None else port
            local = "tcp:{}".format(localport)
            result = self.__run_adb_command(["forward", local, server])
            if result.split(":")[-1] != "":
                return int(result.split(":")[-1])
            else:
                if port is not None:
                    self.remove_forward(port)

    def remove_forward(self, port):
        self.__run_adb_command(["forward", "--remove", "tcp:{}".format(port)])

    @staticmethod
    def list_forward_port():
        output = subprocess.run(
            [ADB_PATH, "forward", "--list"], capture_output=True, text=True
        )
        list_port = output.stdout.split("\n")[:-2]
        return list_port

    @staticmethod
    def list_devices():
        output = ADB.__run_adb_command(ADB(), ["devices"])
        devices = output.split("\n")[1:]
        devices = [device.split("\t")[0] for device in devices if device.strip()]
        return devices

    def install_apk(self, apk_path):
        self.__run_adb_command(["install", apk_path])

    def push_file(self, local_path, device_path):
        self.__run_adb_command(["push", local_path, device_path])

    def get_screen_resolution(self):
        output = self.__run_adb_command(["shell", "wm", "size"])
        return str_to_dict(output.strip())["Physical size"]

    def get_sdk(self):
        output = self.__run_adb_command(["shell", "getprop", "ro.build.version.sdk"])
        return int(output.strip())

    def get_abi(self):
        output = self.__run_adb_command(["shell", "getprop", "ro.product.cpu.abi"])
        return output.strip()

    def swipe(self, start_x, start_y, end_x, end_y, duration=250):
        adb_command = ["shell", "input", "touchscreen", "swipe"]
        adb_command.extend(
            [str(start_x), str(start_y), str(end_x), str(end_y), str(duration)]
        )
        self.__run_adb_command(adb_command)

    def click(self, x: int, y: int, duration=150):
        adb_command = ["shell", "input", "touchscreen", "swipe"]
        adb_command.extend([str(x), str(y), str(x), str(y), str(duration)])
        self.__run_adb_command(adb_command)

    def change_file_permission(self, permission, file_path):
        self.__run_adb_command(["shell", "chmod", permission, file_path])

    def kill_process(self, pid):
        self.__run_adb_command(["shell", "kill", str(pid)])

    def __screencap_raw(self):
        """获取截图源数据"""
        return self.adb_command(["exec-out", "screencap", "-p"])


def str_to_dict(str):
    dict_info = {}
    lines = str.splitlines()
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            dict_info[key.strip()] = value.strip()
    return dict_info





