import threading
import time

from minidevice import MiniDevice
from minidevice.minicap import Minicap
from minidevice.minitouch import Minitouch

a = MiniDevice("emulator-5554", Minicap, None)

s=time.time()
a.screenshot()
print((time.time()-s)*1000)

