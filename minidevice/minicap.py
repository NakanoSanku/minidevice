import os
import socket
import struct
import subprocess
import threading
import time

from minidevice.adb import ADB, ADB_PATH
from minidevice.logger import logger
from minidevice.QueueUtils import PipeQueue
from minidevice.screencap import ScreenCap

WORK_DIR = os.path.dirname(__file__)
MINICAP_PATH = "{}/bin/minicap/libs".format(WORK_DIR)
MINICAPSO_PATH = "{}/bin/minicap/jni".format(WORK_DIR)


def line_breaker(sdk):
    if sdk >= 24:
        line_breaker = os.linesep
    else:
        line_breaker = "\r" + os.linesep
    return line_breaker.encode("ascii")


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
        print(f"connect to {self.__host}:{self.__port}")
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
                        print(self.banner)
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
                        dataBody = dataBody + chunk[cursor : (cursor + frameBodyLength)]
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


class Minicap(ScreenCap):
    def __init__(
        self,
        device,
        rate=15,
        quality=100,
        use_stream=True,
    ) -> None:
        """
        __init__ minicap截图方式

        Args:
            device (str): 设备id
            rate (int, optional): 截图帧率. Defaults to 15.
            quality (int, optional): 截图品质1~100之间. Defaults to 100.
            use_stream (bool, optional): 是否使用stream的方式. Defaults to True.
        """
        self.minicap_adb = ADB(device)
        self.use_stream = use_stream
        self.__get_device_info()
        minicap_name = "minicap_{}".format(time.time())
        minicap_params = {
            "minicap_name": minicap_name,
            "rate": rate,
            "quality": quality,
        }
        self.__get_minicap_params(**minicap_params)
        if self.use_stream:
            self.__start_minicap_by_stream()

    def screencap_raw(self) -> bytes:
        if self.use_stream:
            if self.minicap_popen.poll() is not None:
                logger.warning("尝试重启minicap中")
                self.__stop_minicap_by_stream()
                self.__start_minicap_by_stream()
            logger.debug("screen by minicap stream")
            return self.screen_queue.get()
        else:
            logger.debug("screen by minicap frame")
            return self.__minicap_frame()

    def __minicap_frame(self):
        adb_command = [
            "shell",
            "LD_LIBRARY_PATH=/data/local/tmp",
            "/data/local/tmp/minicap",
        ]
        adb_command.extend(["-P", f"{self.vm_size}@{self.vm_size}/0"])
        adb_command.extend(["-Q", str(self.quality)])
        adb_command.extend(["-s"])
        raw_data = self.minicap_adb.adb_command(adb_command)
        jpg_data = raw_data.split(b"for JPG encoder\n" + line_breaker(self.sdk))[-1]
        jpg_data = jpg_data.replace(line_breaker(self.sdk), b"\n")
        return jpg_data

    def __get_device_info(self):
        self.vm_size = self.minicap_adb.get_screen_resolution()
        self.abi = self.minicap_adb.get_abi()
        self.sdk = self.minicap_adb.get_sdk()

    def __get_minicap_params(self, minicap_name, quality, rate, ip):
        self.minicap_name = minicap_name
        self.quality = quality
        self.rate = rate
        self.ip = ip

    def __minicap_available(func):
        def wrapper(self, *args, **kwargs):
            try:
                adb_command = [
                    "shell",
                    "LD_LIBRARY_PATH=/data/local/tmp",
                    "/data/local/tmp/minicap",
                ]
                adb_command.extend(["-P", f"{self.vm_size}@{self.vm_size}/0"])
                adb_command.extend(["-t"])
                result = self.minicap_adb.adb_command(adb_command).strip()
                if "OK" in result.decode("utf-8"):
                    return func(self, *args, **kwargs)
                return False
            except subprocess.CalledProcessError:
                return False

        return wrapper

    def __minicap_install(self):
        if self.sdk == 32 and self.abi == "x86_64":
            self.abi = "x86"

        MNC_HOME = "/data/local/tmp/minicap"
        MNC_SO_HOME = "/data/local/tmp/minicap.so"

        self.minicap_adb.push_file(f"{MINICAP_PATH}/{self.abi}/minicap", MNC_HOME)
        self.minicap_adb.push_file(
            f"{MINICAPSO_PATH}/android-{self.sdk}/{self.abi}/minicap.so", MNC_SO_HOME
        )
        self.minicap_adb.change_file_permission("+x", MNC_HOME)

    @__minicap_available
    def __start_minicap(self):
        adb_command = [ADB_PATH]
        if self.minicap_adb.device is not None:
            adb_command.extend(["-s", self.minicap_adb.device])
        adb_command.extend(
            ["shell", "LD_LIBRARY_PATH=/data/local/tmp", "/data/local/tmp/minicap"]
        )
        adb_command.extend(["-n", f"{self.minicap_name}"])
        adb_command.extend(["-P", f"{self.vm_size}@{self.vm_size}/0"])
        adb_command.extend(["-Q", str(self.quality)])
        adb_command.extend(["-r", str(self.rate)])
        adb_command.extend(["-S"])
        self.minicap_popen = subprocess.Popen(
            adb_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(2)
        logger.info("启动minicap")
        return True

    def __forward_minicap(self):
        self.minicap_port = self.minicap_adb.forward_port(
            "localabstract:{}".format(self.minicap_name)
        )

    def __read_minicap_stream(self):
        self.minicap_stream = MinicapStream.getBuilder(self.ip, self.minicap_port)
        self.minicap_stream.run()
        self.banner = self.minicap_stream.banner
        self.screen_queue = self.minicap_stream.queue

    def __start_minicap_by_stream(self):
        if not self.__start_minicap():
            self.__minicap_install()
            if not self.__start_minicap():
                raise Exception("minicap不可用")
        self.__forward_minicap()
        self.__read_minicap_stream()

    def __stop_minicap_by_stream(self):
        self.minicap_stream.stop()  # 停止stream
        self.minicap_adb.remove_forward(self.minicap_port)  # 清理端口
        if self.minicap_popen.poll() is None:  # 清理管道
            self.minicap_popen.kill()

    def __del__(self):
        self.__stop_minicap_by_stream()
        
if __name__ == "__main__":
    a = Minicap("127.0.0.1:16384")
    time.sleep(5)
    import cv2

    cv2.imshow("", a.screencap_opencv())
    cv2.waitKey()
