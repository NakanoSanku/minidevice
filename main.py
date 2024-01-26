import threading
import time

import adbutils

from minidevice import MiniDevice
from minidevice.minicap import MiniCap
from minidevice.minitouch import MiniTouch
from minidevice.maatouch import MaaTouch
#
a = MiniDevice("127.0.0.1:16384", None, MaaTouch)


# x = 100 y=620
# x =y  y= max_y - x

a.click(200, 400, 5000)
# output = adbutils.adb.device("127.0.0.1:16384").shell()
# # 获取屏幕方向
# # 获取屏幕分辨率
# print(output)
# |grep 'mCurrentOrientation='
# |grep ''
# output = adbutils.adb.device("127.0.0.1:16384").shell("dumpsys input")
# print(output)
