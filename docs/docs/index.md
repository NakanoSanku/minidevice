# Welcome to MiniDevice

⭐ star my  [project](https://github.com/NakanoSanku/minidevice).(~~算我求你了~~)

## Installation

```shell
pip install minidevice
```

## Project Structure
- MiniDevice
    - screencap
        - Minicap
        - ADBcap
        - DroidCast
        - ScrcpyCap
    - touch
        - Minitouch
        - ADBtouch
        - ScrcpyTouch

阅读下面部分之前先阅读API文档
## Q&A
Q: 设备id是什么

A: adb devices 每行的第一个字段

Q: scrcpy.Client是什么

A: 通过scrcpy.Client()创建的对象
> 具体参考 https://github.com/leng-yue/py-scrcpy-client

scrcpy.Client()简要参数说明

- device 设备id
- max_width 最大宽度
- bitrate 码率
- max_fps 最大帧率


