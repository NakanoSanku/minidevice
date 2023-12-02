# minidevice
一个对安卓设备(主要是安卓模拟器)进行基础操作的工具包
## 更新日志
### 2023.12.2 
更新README说明,添加[MiniDevice](./minidevice/device.py)类
### 2023.8.10 
移除opencv库的引用，让用户自行处理截图源数据bytes,以此减少库依赖(opencv，numpy库真的很大且并非所有人都需要)
## requirements
[`pyminitouch`](https://github.com/williamfzc/pyminitouch) `adbutils==1.2.9`
## 安装
`pip install minidevice`
## API文档以及使用说明
大致设计思路就是通过实现`ScreenCap`和`Touch`这两个抽象基类
1. ScreenCap 
- @abstractmethod screencap_raw 返回截图bytes数据
- save_screencap(path) 保存截图到path 
2. Touch
- @abstractmethod click(x,y,duration) 
- @abstractmethod swipe(points,duraiton)

整合至MiniDevice类创建对安卓设备操作的对象,引入基础操作锁，防止不合理并发导致的程序错误
> User无需关心具体实现过程，Developer直接继承基类即可添加新方法

### 已实现的特性
- ScreenCap
    - Minicap
    - ADBcap
    - DroidCast

- Touch
    - Minitouch
    - ADBtouch
## 已知bug
- [ ] 转发端口清理失败
- [ ] pyminitouch库使用系统路径的adb，导致需用户自行安装adb工具并添加到环境变量中
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
