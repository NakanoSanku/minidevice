import json
import socket
import subprocess
import threading
import time

from adbutils import adb

from minidevice.config import MINICAP_PATH, MINICAPSO_PATH, ADB_EXECUTOR, MNC_HOME, MNC_SO_HOME, MINICAP_COMMAND, \
    MINICAP_START_TIMEOUT,DEFAULT_HOST
from minidevice.screencap.screencap import ScreenCap
from minidevice.utils.logger import logger


class MinicapStream:
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.data = None
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.read_stream, daemon=True)

    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
        except ConnectionRefusedError:
            logger.error(
                f"Be sure to run `adb forward tcp:{self.port} localabstract:minicap`")
            return

        self.thread.start()

    def read_stream(self):
        banner = {
            'version': 0,
            'length': 0,
            'pid': 0,
            'realWidth': 0,
            'realHeight': 0,
            'virtualWidth': 0,
            'virtualHeight': 0,
            'orientation': 0,
            'quirks': 0
        }

        read_banner_bytes = 0
        banner_length = 2
        read_frame_bytes = 0
        frame_body_length = 0
        frame_body = bytearray()
        max_bufsize = 4096

        while not self.stop_event.is_set():
            chunk = self.sock.recv(max_bufsize)
            if not chunk:
                break

            # logger.info(f"chunk(length={len(chunk)})", )
            cursor = 0
            while cursor < len(chunk):
                if read_banner_bytes < banner_length:
                    if read_banner_bytes == 0:
                        banner['version'] = chunk[cursor]
                    elif read_banner_bytes == 1:
                        banner['length'] = banner_length = chunk[cursor]
                    elif 2 <= read_banner_bytes <= 5:
                        banner['pid'] += (chunk[cursor] <<
                                          ((read_banner_bytes - 2) * 8)) & 0xFFFFFFFF
                    elif 6 <= read_banner_bytes <= 9:
                        banner['realWidth'] += (chunk[cursor] <<
                                                ((read_banner_bytes - 6) * 8)) & 0xFFFFFFFF
                    elif 10 <= read_banner_bytes <= 13:
                        banner['realHeight'] += (chunk[cursor] <<
                                                 ((read_banner_bytes - 10) * 8)) & 0xFFFFFFFF
                    elif 14 <= read_banner_bytes <= 17:
                        banner['virtualWidth'] += (chunk[cursor] <<
                                                   ((read_banner_bytes - 14) * 8)) & 0xFFFFFFFF
                    elif 18 <= read_banner_bytes <= 21:
                        banner['virtualHeight'] += (chunk[cursor] <<
                                                    ((read_banner_bytes - 18) * 8)) & 0xFFFFFFFF
                    elif read_banner_bytes == 22:
                        banner['orientation'] = chunk[cursor] * 90
                    elif read_banner_bytes == 23:
                        banner['quirks'] = chunk[cursor]

                    cursor += 1
                    read_banner_bytes += 1

                    if read_banner_bytes == banner_length:
                        logger.info(f"banner {banner}",)
                elif read_frame_bytes < 4:
                    frame_body_length += (chunk[cursor] <<
                                          (read_frame_bytes * 8)) & 0xFFFFFFFF
                    cursor += 1
                    read_frame_bytes += 1
                    # logger.info(f"headerbyte{read_frame_bytes}(val={frame_body_length})")
                else:
                    max_bufsize = frame_body_length
                    if len(chunk) - cursor >= frame_body_length:
                        frame_body.extend(
                            chunk[cursor:cursor + frame_body_length])
                        if frame_body[0] != 0xFF or frame_body[1] != 0xD8:
                            logger.error(
                                f"Frame body does not start with JPG header {frame_body}", )
                            return
                        self.data = frame_body
                        cursor += frame_body_length
                        frame_body_length = read_frame_bytes = 0
                        frame_body = bytearray()
                    else:
                        frame_body.extend(chunk[cursor:])
                        frame_body_length -= len(chunk) - cursor
                        read_frame_bytes += len(chunk) - cursor
                        cursor = len(chunk)

    def stop(self):
        logger.info("Stopping the stream")
        self.stop_event.set()
        self.sock.close()
        self.thread.join()

    def nextImage(self):
        self.data = None
        while not self.data:
            continue
        return self.data


class MiniCapUnSupportError(Exception):
    pass


class MiniCap(ScreenCap):
    def __init__(
            self,
            serial,
            rate=None,
            quality=100,
            skip_frame=True,
            use_stream=True,
            host=DEFAULT_HOST
    ):
        """
        __init__ minicap截图方式

        Args:
            serial (str): 设备id
            rate (int, optional): 截图帧率. Defaults to 自动获取.
            quality (int, optional): 截图品质1~100之间. Defaults to 100.
            skip_frame(bool,optional): 当无法快速获得截图时，跳过这个帧
            use_stream (bool, optional): 是否使用stream的方式. Defaults to True.
        """
        self.__adb = adb.device(serial)
        self.__skip_frame = skip_frame
        self.__use_stream = use_stream
        self.__quality = quality
        self.__rate = rate
        self.__host = host
        self.__get_device_info()

        self.__minicap_kill()
        self.__minicap_install()
        self.__get_device_input_info()
        if self.__use_stream:
            self.__start_minicap_by_stream()

    def screencap_raw(self) -> bytes:
        if self.__use_stream:
            return self.__minicap_stream.nextImage()
        else:
            return self.__minicap_frame()

    def __minicap_frame(self):
        adb_command = MINICAP_COMMAND+[]
        adb_command.extend(
            ["-P", f"{self.__vm_size}@{self.__vm_size}/{self.__rotation}"])
        adb_command.extend(["-Q", str(self.__quality)])
        adb_command.extend(["-s"])
        raw_data = self.__adb.shell(adb_command, encoding=None)
        jpg_data = raw_data.split(b"for JPG encoder\n")[-1]
        return jpg_data

    def __minicap_kill(self):
        self.__adb.shell(['pkill', '-9', 'minicap'])

    def __get_device_input_info(self):
        try:
            # 通过 -i 参数获取屏幕信息
            command = MINICAP_COMMAND + ["-i"]
            info_result = self.__adb.shell(command)
            # 找到JSON数据的起始位置
            start_index = info_result.find('{')
            # 提取JSON字符串
            if start_index != -1:
                extracted_json = info_result[start_index:]
                logger.info(extracted_json)
            else:
                raise MiniCapUnSupportError("minicap does not support")
            info = json.loads(extracted_json)
            self.__vm_size = self.__adb.shell("wm size").split(" ")[-1]
            self.__rotation = info.get("rotation")
            self.__rate = info.get(
                "fps") if self.__rate is None else self.__rate
        except Exception as e:
            raise MiniCapUnSupportError("minicap does not support")

    def __get_device_info(self):
        self.__abi = self.__adb.getprop("ro.product.cpu.abi")
        self.__sdk = self.__adb.getprop("ro.build.version.sdk")

    def __minicap_install(self):
        """安装minicap"""
        if str(self.__sdk) == "32" and str(self.__abi) == "x86_64":
            self.__abi = "x86"
        if int(self.__sdk) > 34:
            raise MiniCapUnSupportError("minicap does not support Android 12+")
        self.__adb.sync.push(f"{MINICAP_PATH}/{self.__abi}/minicap", MNC_HOME)
        self.__adb.sync.push(
            f"{MINICAPSO_PATH}/android-{self.__sdk}/{self.__abi}/minicap.so", MNC_SO_HOME
        )
        self.__adb.shell(["chmod +x", MNC_HOME])

    def __start_minicap(self):
        adb_command = [ADB_EXECUTOR]
        if self.__adb.serial is not None:
            adb_command.extend(["-s", self.__adb.serial])
        adb_command.extend(["shell"])
        adb_command.extend(MINICAP_COMMAND)
        adb_command.extend(
            ["-P", f"{self.__vm_size}@{self.__vm_size}/{self.__rotation}"])
        adb_command.extend(["-Q", str(self.__quality)])
        adb_command.extend(["-r", str(self.__rate)])
        if self.__skip_frame:
            adb_command.extend(["-S"])
        logger.info(adb_command)
        self.__minicap_popen = subprocess.Popen(
            adb_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        logger.info("minicap connection takes a long time, please be patient.")
        for i in range(MINICAP_START_TIMEOUT):
            logger.info("minicap starting by {}s".format(
                MINICAP_START_TIMEOUT - i))
            time.sleep(1)
        return True

    def __forward_minicap(self):
        self.minicap_port = self.__adb.forward_port("localabstract:minicap")

    def __read_minicap_stream(self):
        self.__minicap_stream = MinicapStream(self.__host, self.minicap_port)
        self.__minicap_stream.start()

    def __start_minicap_by_stream(self):
        self.__start_minicap()
        self.__forward_minicap()
        self.__read_minicap_stream()

    def __stop_minicap_by_stream(self):
        if self.__use_stream:
            self.__minicap_stream.stop()  # 停止stream
            if self.__minicap_popen.poll() is None:  # 清理管道
                self.__minicap_popen.kill()

    def __del__(self):
        self.__stop_minicap_by_stream()
