import time

from minidevice import *
from minidevicemumuapi import *

# MuMuScreenCap(0, r"D:\MuMuPlayer-12.0")
# 创建一个MiniDevice实例
# "127.0.0.1:16384"
# emulator-5554
a = MiniDevice("127.0.0.1:16384", None, MiniTouch, 0)


a.click(200, 100, 5000)

print("helloworld")

