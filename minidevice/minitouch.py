import os
import time
import subprocess
import socket
import os

from adbutils import adb

from minidevice.logger import logger
from minidevice import config
from minidevice.touch import Touch
from minidevice.utils import str2byte

WORK_DIR = os.path.dirname(__file__)
MINITOUCH_PATH = "{}/bin/minitouch/libs".format(WORK_DIR)
MINITOUCH_REMOTE_PATH = "/data/local/tmp/minitouch"
_ADB = config.ADB_EXECUTOR
MINITOUCH_REMOTE_ADDR = "localabstract:minitouch"
MINITOUCH_SERVER_START_DELAY = 1


class CommandBuilder(object):
    """Build command str for minitouch.

    You can use this, to custom actions as you wish::

        with safe_connection(_DEVICE_ID) as connection:
            builder = CommandBuilder()
            builder.down(0, 400, 400, 50)
            builder.commit()
            builder.move(0, 500, 500, 50)
            builder.commit()
            builder.move(0, 800, 400, 50)
            builder.commit()
            builder.up(0)
            builder.commit()
            builder.publish(connection)

    use `d.connection` to get `connection` from device
    """

    # TODO (x, y) can not beyond the screen size
    def __init__(self):
        self._content = ""
        self._delay = 0

    def append(self, new_content):
        self._content += new_content + "\n"

    def commit(self):
        """add minitouch command: 'c\n'"""
        self.append("c")

    def wait(self, ms):
        """add minitouch command: 'w <ms>\n'"""
        self.append("w {}".format(ms))
        self._delay += ms

    def up(self, contact_id):
        """add minitouch command: 'u <contact_id>\n'"""
        self.append("u {}".format(contact_id))

    def down(self, contact_id, x, y, pressure):
        """add minitouch command: 'd <contact_id> <x> <y> <pressure>\n'"""
        self.append("d {} {} {} {}".format(contact_id, x, y, pressure))

    def move(self, contact_id, x, y, pressure):
        """add minitouch command: 'm <contact_id> <x> <y> <pressure>\n'"""
        self.append("m {} {} {} {}".format(contact_id, x, y, pressure))

    def publish(self, connection):
        """apply current commands (_content), to your device"""
        self.commit()
        final_content = self._content
        logger.info("send operation: {}".format(final_content.replace("\n", "\\n")))
        connection.send(final_content)
        time.sleep(self._delay / 1000 + config.DEFAULT_DELAY)
        self.reset()

    def reset(self):
        """clear current commands (_content)"""
        self._content = ""
        self._delay = 0


class MiniTouchUnSupportError(Exception):
    pass


class MiniTouch(Touch):
    def __init__(self, serial):
        """
        __init__ minitouch点击方式

        Args:
            device (str): 设备id
        """
        self.minitouch_process = None  # minitouch服务进程
        self.minitouch_port = None  # Socket端口记录
        self.pid = None  # minitouch服务pid记录
        self.__adb = adb.device(serial)  # adb设备

        self.__get_device_info()  # 获取设备信息
        self.__minitouch_install()  # 安装minitouch
        self.__kill_minitouch_server()  # 终止设备上正在运行的minitouch服务

        self.start()  # 启动minitouch

    def __start_minitouch_server(self):
        """启动安卓设备Minitouch Server"""
        command_list = [
            _ADB,
            "-s",
            self.__adb.serial,
            "shell",
            "/data/local/tmp/minitouch",
        ]
        # 如果minitouch进程没有运行过
        if self.minitouch_process is None:
            logger.info("start minitouch: {}".format(" ".join(command_list)))
            self.minitouch_process = subprocess.Popen(
                command_list, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        time.sleep(MINITOUCH_SERVER_START_DELAY)  # 等待Minitouch启动完成
        self.minitouch_port = self.__adb.forward_port(MINITOUCH_REMOTE_ADDR)  # 转发端口
        # TODO 检查minitouch是否可用

    def __connect_minitouch_by_socket(self):
        """使用TCP连接minitouch"""
        # build connection
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((config.DEFAULT_HOST, self.minitouch_port))  # 连接转发的端口
        self.client = client
        # get minitouch server info
        socket_out = client.makefile()
        # v <version>
        # protocol version, usually it is 1. needn't use this
        socket_out.readline()
        # ^ <max-contacts> <max-x> <max-y> <max-pressure>
        _, self.max_contacts, self.max_x, self.max_y, self.max_pressure, *_ = (
            socket_out.readline().replace("\n", "").replace("\r", "").split(" ")
        )

        # $ <pid>
        _, self.pid = (
            socket_out.readline().replace("\n", "").replace("\r", "").split(" ")
        )
        logger.info(
            "minitouch running on port: {}, pid: {}".format(
                self.minitouch_port, self.pid
            )
        )
        logger.info(
            "max_contact: {}; max_x: {}; max_y: {}; max_pressure: {}".format(
                self.max_contacts, self.max_x, self.max_y, self.max_pressure
            )
        )

    def __disconnect_minitouch_socket(self):
        """关闭Socket连接"""
        self.client and self.client.close()
        self.client = None
        logger.info("minitouch disconnected")

    def send(self, content):
        """send message and get its response"""
        byte_content = str2byte(content)
        self.client.sendall(byte_content)
        return self.client.recv(config.DEFAULT_BUFFER_SIZE)

    def __kill_minitouch_server(self):
        if self.minitouch_process and self.minitouch_process.poll() is None:
            self.minitouch_process.kill()
            self.minitouch_process = None
        if self.pid is None:
            self.pid = self.__adb.shell(["pidof", "minitouch"]).strip()
        if self.pid:
            self.__adb.shell(["kill", self.pid])
            self.pid = None

    def __get_device_info(self):
        """获取设备信息"""
        self.__abi = self.__adb.getprop("ro.product.cpu.abi")  # 获取设备架构
        self.__sdk = self.__adb.getprop("ro.build.version.sdk")  # 获取设备sdk
        self.__orientation = self.__adb.rotation()  # 屏幕方向获取
        self.__window_size = self.__adb.window_size()
        self.__width = self.__window_size.width
        self.__height = self.__window_size.height
        logger.debug(f"\n屏幕方向:{self.__orientation}\n屏幕宽度:{self.__width}\n屏幕高度:{self.__height}")

    def __minitouch_install(self):
        self.__adb.sync.push(
            f"{MINITOUCH_PATH}/{self.__abi}/minitouch", MINITOUCH_REMOTE_PATH
        )
        self.__adb.shell(f"chmod +x {MINITOUCH_REMOTE_PATH}")

    def start(self):
        """启动minitouch服务"""
        # 启动minitouch Server
        self.__start_minitouch_server()
        # 构建tcp连接socket
        self.__connect_minitouch_by_socket()

    def stop(self):
        """停止minitouch服务"""
        # 关闭TCP连接
        self.__disconnect_minitouch_socket()
        # 终止minitouch服务
        self.__kill_minitouch_server()

    def __tap(self, points, pressure=100, duration=None, no_up=None):
        """
        tap on screen, with pressure/duration

        :param points: list, looks like [(x1, y1), (x2, y2)]
        :param pressure: default == 100
        :param duration:
        :param no_up: if true, do not append 'up' at the end
        :return:
        """
        points = [self.__convert(point[0], point[1]) for point in points]
        points = [list(map(int, each_point)) for each_point in points]

        _builder = CommandBuilder()
        for point_id, each_point in enumerate(points):
            x, y = each_point
            _builder.down(point_id, x, y, pressure)
        _builder.commit()

        # apply duration
        if duration:
            _builder.wait(duration)
            _builder.commit()

        # need release?
        if not no_up:
            for each_id in range(len(points)):
                _builder.up(each_id)

        _builder.publish(self)

    def __swipe(self, points, pressure=100, duration=None, no_down=None, no_up=None):
        """
        swipe between points, one by one

        :param points: [(400, 500), (500, 500)]
        :param pressure: default == 100
        :param duration:
        :param no_down: will not 'down' at the beginning
        :param no_up: will not 'up' at the end
        :return:
        """
        points = [self.__convert(point[0], point[1]) for point in points]
        points = [list(map(int, each_point)) for each_point in points]

        _builder = CommandBuilder()
        point_id = 0

        # tap the first point
        if not no_down:
            x, y = points.pop(0)
            _builder.down(point_id, x, y, pressure)
            _builder.publish(self)

        # start swiping
        for each_point in points:
            x, y = each_point
            _builder.move(point_id, x, y, pressure)

            # add delay between points
            if duration:
                _builder.wait(duration)
            _builder.commit()

        _builder.publish(self)

        # release
        if not no_up:
            _builder.up(point_id)
            _builder.publish(self)

    def __convert(self, x, y):
        if self.__orientation == 0:
            pass
        elif self.__orientation == 1:
            x, y = self.__height - y, x
        elif self.__orientation == 2:
            x, y = self.__width - x, self.__height - y
        elif self.__orientation == 3:
            x, y = y, self.__width - x
        return x, y

    def click(self, x: int, y: int, duration: int = 100):
        self.__tap([(x, y)], duration=duration)

    def swipe(self, points: list, duration: int = 300):
        self.__swipe(points, duration=duration / (len(points) - 1))

    def __del__(self):
        self.stop()
