# minidevice
一个对安卓设备(主要是安卓模拟器)进行基础操作的工具包
## requirements
`opencv-python` [`pyminitouch`](https://github.com/williamfzc/pyminitouch)
## 安装
`pip install minidevice`
## API文档以及使用说明
[跳转](https://nakanosanku.github.io/minidevice/)
## 已知bug
- [ ] 转发端口清理失败
## Feature
- screencap
    - Minicap
    - ADBcap
    - DroidCast

- touch
    - Minitouch
    - ADBtouch

## 性能排序
### 截图
Minicap>>DroidCast>>ADBcap

- Minicap截取一张图片时间大概`20~30ms`,当然你可以通过添加参数rate，以获得更加高的速度(但这同时会拉高设备CPU占用)
- DroidCast截图图片时间大概在`100ms`以内，场景越复杂,时间越长,解决方法未知
- ADBcap耗时`500ms`甚至更长,稳定性未知

### 触控
Minitouch>>ADBtouch
- Minitouch触控效率据说和Windows api几乎相同
- ADBtouch无法模拟曲线滑动,只能点到点直线
