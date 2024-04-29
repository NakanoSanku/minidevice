from minidevice import MiniDevice
from minidevice.minicap import MiniCap
from minidevice.minitouch import MiniTouch
from minidevice.maatouch import MaaTouch
from minidevice.DroidCast import DroidCast
from minidevice.adbcap import ADBCap
from minidevice.adbtouch import ADBTouch
#
a = MiniDevice("127.0.0.1:16384", DroidCast, None)


a.save_screenshot("./screenshot.png")
a.click(200, 400, 5000)
