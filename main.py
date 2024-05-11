from minidevice import MiniDevice
from minidevice.minicap import MiniCap
from minidevice.minitouch import MiniTouch
from minidevice.maatouch import MaaTouch
from minidevice.DroidCast import DroidCast
from minidevice.adbcap import ADBCap
from minidevice.adbtouch import ADBTouch
#
a = MiniDevice("emulator-5554", DroidCast, MiniTouch)


a.save_screenshot("./screenshot.png")
a.click(200, 400, 5000)
print(a.width())