> 所有截图类基于ScreenCap,所以他们截图方法与ScreenCap相同
::: minidevice.screencap

::: minidevice.minicap
```python
from minidevice import Minicap
#创建截图对象
capdevice = Minicap("127.0.0.1:16834")
#获取opencv格式截图
cap = capdevice.screen_opencv()
#获取raw格式截图
cap = capdevice.screen_raw()
#截图并保存本地
capdevice.save_screen()
```
::: minidevice.DroidCast
```python
from minidevice import DroidCast
#创建截图对象
capdevice = DroidCast("127.0.0.1:16834")
#获取opencv格式截图
cap = capdevice.screen_opencv()
#获取raw格式截图
cap = capdevice.screen_raw()
#截图并保存本地
capdevice.save_screen()
```
::: minidevice.adbcap
```python
from minidevice import ADBcap
#创建截图对象
capdevice = ADBcap("127.0.0.1:16834")
#获取opencv格式截图
cap = capdevice.screen_opencv()
#获取raw格式截图
cap = capdevice.screen_raw()
#截图并保存本地
capdevice.save_screen()
```
::: minidevice.scrcpycap
```python
from minidevice import ScrcpyCap
import scrcpy
#创建截图对象
device=scrcpy.Client("127.0.0.1:16834")
capdevice = ScrcpyCap(device)
#获取opencv格式截图
cap = capdevice.screen_opencv()
#获取raw格式截图
cap = capdevice.screen_raw()
#截图并保存本地
capdevice.save_screen()
```
