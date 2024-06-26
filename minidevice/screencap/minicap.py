import json
import socket
import struct
import subprocess
import threading
import time

from adbutils import adb

from minidevice.config import MINICAP_PATH, MINICAPSO_PATH, ADB_EXECUTOR, MNC_HOME, MNC_SO_HOME, MINICAP_COMMAND, \
    MINICAP_START_TIMEOUT
from minidevice.screencap.screencap import ScreenCap
from minidevice.utils.logger import logger
from minidevice.utils.queue_utils import PipeQueue


class Banner:
    def __init__(self):
        self.Version = 0  # 版本信息
        self.Length = 0  # banner长度
        self.Pid = 0  # 进程ID
        self.RealWidth = 0  # 设备的真实宽度
        self.RealHeight = 0  # 设备的真实高度
        self.VirtualWidth = 0  # 设备的虚拟宽度
        self.VirtualHeight = 0  # 设备的虚拟高度
        self.Orientation = 0  # 设备方向
        self.Quirks = 0  # 设备信息获取策略

    def __str__(self):
        message = (
                "Banner [Version="
                + str(self.Version)
                + ", length="
                + str(self.Length)
                + ", Pid="
                + str(self.Pid)
                + ", realWidth="
                + str(self.RealWidth)
                + ", realHeight="
                + str(self.RealHeight)
                + ", virtualWidth="
                + str(self.VirtualWidth)
                + ", virtualHeight="
                + str(self.VirtualHeight)
                + ", orientation="
                + str(self.Orientation)
                + ", quirks="
                + str(self.Quirks)
                + "]"
        )
        return message

    def set_of_bytes(self, data):
        (
            self.Version,
            self.Length,
            self.Pid,
            self.RealWidth,
            self.RealHeight,
            self.VirtualWidth,
            self.VirtualHeight,
            self.Orientation,
            self.Quirks,
        ) = struct.unpack("<2b5ibB", data)


class MinicapStream:
    __instance = {}
    __mutex = threading.Lock()

    def __init__(self, host: str, port: int, queue: PipeQueue):
        self.buffer_size = 4096
        self.__host = host  # socket 主机
        self.__port = port  # socket 端口
        self.banner = Banner()  # 用于存放banner头信息
        self.running = False
        self.__pid = 0  # 进程ID
        self.minicapSocket = None
        self.ReadImageStreamTask = None
        self.queue = queue  # 图像数据队列

    @staticmethod
    def getBuilder(host: str, port: int, size=5) -> "MinicapStream":
        key = f"{host}:{port}"
        if key not in MinicapStream.__instance:
            MinicapStream.__mutex.acquire()
            if key not in MinicapStream.__instance:
                MinicapStream.__instance[key] = MinicapStream(
                    host, port, PipeQueue(maxsize=size)
                )
            MinicapStream.__mutex.release()
        return MinicapStream.__instance[key]

    def run(self):
        # 开始执行
        # 启动socket连接
        self.minicapSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 定义socket类型，网络通信，TCP
        self.minicapSocket.connect((self.__host, self.__port))
        logger.info(f"connect to {self.__host}:{self.__port}")
        self.ReadImageStreamTask = threading.Thread(target=self.ReadImageStream)
        self.ReadImageStreamTask.daemon = True
        self.running = True
        self.ReadImageStreamTask.start()

    def ReadImageStream(self):
        # 读取图片流到队列
        bannerLength = 24
        readBannerBytes = 0

        readFrameBytes = 0
        frameBodyLength = 0
        dataBody = b""
        while self.running:
            chunk = self.minicapSocket.recv(4096)
            length = len(chunk)
            if not length:
                continue
            cursor = 0
            while cursor < length:
                # 读取 Banner
                if readBannerBytes < bannerLength:
                    if readBannerBytes == 0:
                        self.banner.Version = chunk[cursor]
                    elif readBannerBytes == 1:
                        bannerLength = chunk[cursor]
                        self.banner.Length = bannerLength
                    elif readBannerBytes in [2, 3, 4, 5]:
                        self.banner.Pid += (
                                                   chunk[cursor] << ((readBannerBytes - 2) * 8)
                                           ) >> 0
                    elif readBannerBytes in [6, 7, 8, 9]:
                        self.banner.RealWidth += (
                                                         chunk[cursor] << ((readBannerBytes - 6) * 8)
                                                 ) >> 0
                    elif readBannerBytes in [10, 11, 12, 13]:
                        self.banner.RealHeight += (
                                                          chunk[cursor] << ((readBannerBytes - 10) * 8)
                                                  ) >> 0
                    elif readBannerBytes in [14, 15, 16, 17]:
                        self.banner.VirtualWidth += (
                                                            chunk[cursor] << ((readBannerBytes - 14) * 8)
                                                    ) >> 0
                    elif readBannerBytes in [18, 19, 20, 21]:
                        self.banner.VirtualHeight += (
                                                             chunk[cursor] << ((readBannerBytes - 18) * 8)
                                                     ) >> 0
                    elif readBannerBytes == 22:
                        self.banner.Orientation = chunk[cursor] * 90
                    elif readBannerBytes == 23:
                        self.banner.Quirks = chunk[cursor]
                    cursor += 1
                    readBannerBytes += 1
                    if readBannerBytes == bannerLength:
                        logger.info(self.banner)
                # 读取图片大小数据
                elif readFrameBytes < 4:
                    frameBodyLength = frameBodyLength + (
                            (chunk[cursor] << (readFrameBytes * 8)) >> 0
                    )
                    cursor += 1
                    readFrameBytes += 1
                # 读取图片内容
                else:
                    if length - cursor >= frameBodyLength:
                        dataBody = dataBody + chunk[cursor: (cursor + frameBodyLength)]
                        if dataBody[0] != 0xFF or dataBody[1] != 0xD8:
                            return
                        self.queue.put(dataBody)
                        cursor += frameBodyLength
                        frameBodyLength = 0
                        readFrameBytes = 0
                        dataBody = b""
                    else:
                        dataBody = dataBody + chunk[cursor:length]
                        frameBodyLength -= length - cursor
                        readFrameBytes += length - cursor
                        cursor = length

    def stop(self):
        self.running = False
        if self.ReadImageStreamTask:
            self.ReadImageStreamTask.join()  # 等待读取图像流的线程结束
        if self.minicapSocket:
            self.minicapSocket.close()  # 关闭 minicap 的 socket 连接


class MiniCapUnSupportError(Exception):
    pass


class MiniCap(ScreenCap):
    def __init__(
            self,
            serial,
            rate=None,
            quality=100,
            skip_frame=False,
            use_stream=True,
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
        self.__get_device_info()

        self.__minicap_kill()
        self.__minicap_install()
        self.__get_device_input_info()
        if self.__use_stream:
            self.__start_minicap_by_stream()

    def screencap_raw(self) -> bytes:
        if self.__use_stream:
            return self.__screen_queue.get()
        else:
            return self.__minicap_frame()

    def __minicap_frame(self):
        adb_command = MINICAP_COMMAND+[]
        adb_command.extend(["-P", f"{self.__vm_size}@{self.__vm_size}/{self.__rotation}"])
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
            self.__rate = info.get("fps") if self.__rate is None else self.__rate
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
        adb_command.extend(["-P", f"{self.__vm_size}@{self.__vm_size}/{self.__rotation}"])
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
            logger.info("minicap starting by {}s".format(MINICAP_START_TIMEOUT - i))
            time.sleep(1)
        return True

    def __forward_minicap(self):
        self.minicap_port = self.__adb.forward_port("localabstract:minicap")

    def __read_minicap_stream(self):
        self.__minicap_stream = MinicapStream.getBuilder("127.0.0.1", self.minicap_port)
        self.__minicap_stream.run()
        self.__banner = self.__minicap_stream.banner
        self.__screen_queue = self.__minicap_stream.queue

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
