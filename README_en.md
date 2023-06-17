# minidevice
A toolkit for basic operations on Android devices (mainly Android emulators).

Due to the lack of some foundations, the `whl` file provides users with static resources such as adb tools, minicap, and minitouch, making it convenient for users with poor network conditions to use them normally.

Due to the high CPU usage of uiautomator when taking screenshots and the lack of updates to uiautomator for a long time, this method has been removed.

## Requirements
`opencv-python`, [`pyminitouch`](https://github.com/williamfzc/pyminitouch)

## Installation
```shell
pip install minidevice
```

## Usage Example

```python
from minidevice import Minicap
#创建截图对象
capdevice = Minicap("127.0.0.1:16834")
#截图
cap = capdevice.screen_opencv()
#截图并保存本地
capdevice.save_screen()
```

```python
from minidevice import Minitouch
#创建截图对象
touchdevice = Minitouch("127.0.0.1:16834")
#点击
touchdevice.click(x=101,y=101,duration=150)
#长按
touchdevice.click(x=101,y=101,duration=500)
#滑动
touchdevice.swipe([(100,100),(500,500)])
```
