> 所有截图类基于Touch,所以他们操作方法与Touch相同

::: minidevice.touch

::: minidevice.minitouch
```py
from minidevice import Minitouch
#创建操作对象
touchdevice = Minitouch("127.0.0.1:16834")
#点击
touchdevice.click(x=101,y=101,duration=150)
#长按
touchdevice.click(x=101,y=101,duration=500)
#滑动
touchdevice.swipe([(100,100),(500,500)])
```
::: minidevice.adbtouch
```py
from minidevice import ADBtouch
#创建操作对象
touchdevice = ADBtouch("127.0.0.1:16834")
#点击
touchdevice.click(x=101,y=101,duration=150)
#长按
touchdevice.click(x=101,y=101,duration=500)
#滑动
touchdevice.swipe([(100,100),(500,500)])
```
::: minidevice.scrcpytouch
```py
from minidevice import ScrcpyTouch
import scrcpy
#创建操作对象
device=scrcpy.Client("127.0.0.1:16834")
touchdevice = ScrcpyTouch(device)
#点击
touchdevice.click(x=101,y=101,duration=150)
#长按
touchdevice.click(x=101,y=101,duration=500)
#滑动
touchdevice.swipe([(100,100),(500,500)])
```