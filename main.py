from minidevice import MiniDevice
from minidevice.minicap import Minicap
from minidevice.minitouch import Minitouch
a=MiniDevice("emulator-5554",Minicap,Minitouch)
a.screenshot()
with open("a.png", "wb") as fp:
    fp.write(a.screenshot())
a.click(100,100)
a.swipe([(10,10),(100,100)])