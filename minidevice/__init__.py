from minidevice.DroidCast import DroidCast
from minidevice.adbcap import ADBcap
from minidevice.adbtouch import ADBtouch
from minidevice.minicap import Minicap
from minidevice.minitouch import Minitouch
from minidevice.screencap import ScreenCap
from minidevice.touch import Touch

TOUCH_METHOD = {
    "Minitouch":Minitouch,
    "ADBtouch":ADBtouch
}

CAP_METHOD = {
    "ADBcap": ADBcap,
    "Minicap": Minicap,
    "DroidCast": DroidCast
}
