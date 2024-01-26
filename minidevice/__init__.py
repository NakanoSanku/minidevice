from minidevice.DroidCast import DroidCast
from minidevice.adbcap import ADBCap
from minidevice.adbtouch import ADBTouch
from minidevice.minicap import MiniCap
from minidevice.minitouch import MiniTouch
from minidevice.maatouch import MaaTouch
from minidevice.screencap import ScreenCap
from minidevice.touch import Touch
from minidevice.device import MiniDevice
import minidevice.logger

CAP_METHOD = {
    'adb': ADBCap,
    'minicap': MiniCap,
    'DroidCast': DroidCast,
}

TOUCH_METHOD = {
    'adb': ADBTouch,
    'minitouch': MiniTouch,
    'MaaTouch': MaaTouch
}