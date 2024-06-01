from minidevice.screencap.droidcast import DroidCast
from minidevice.screencap.adbcap import ADBCap
from minidevice.touch.adbtouch import ADBTouch
from minidevice.screencap.minicap import MiniCap
from minidevice.touch.minitouch import MiniTouch
from minidevice.touch.maatouch import MaaTouch
from minidevice.screencap.screencap import ScreenCap
from minidevice.touch.touch import Touch
from minidevice.device import MiniDevice

CAP_METHOD = {
    'adb': ADBCap,
    'MiniCap': MiniCap,
    'DroidCast': DroidCast,
}

TOUCH_METHOD = {
    'adb': ADBTouch,
    'MiniTouch': MiniTouch,
    'MaaTouch': MaaTouch
}
