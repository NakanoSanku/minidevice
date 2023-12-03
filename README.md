# minidevice
一个对安卓设备(主要是安卓模拟器)进行基础操作的工具包
## 项目结构
- **Root Directory**
  - `README.md`
  - `main.py`
  - `requirements.txt`
  - `setup.py`

- **minidevice/**
  - `__init__.py`
  - `DroidCast.py`
  - `QueueUtils.py`
  - `adbcap.py`
  - `adbtouch.py`
  - `device.py`
  - `logger.py`
  - `minicap.py`
  - `minitouch.py`
  - `screencap.py`
  - `touch.py`
  - **bin/**
    - `DroidCast-debug-1.1.1.apk`
    - **minicap/jni/**
      - *Various `minicap.so` files for different Android versions and architectures*
    - **minicap/libs/**
      - *Various `minicap` binaries for different architectures*
    - **minitouch/libs/**
      - *Various `minitouch` binaries for different architectures*

- **tests/**
  - `test_minidevice.py`

## 更新日志
### 2023.12.3 
屏蔽pyminitouch的日志并在MiniDevice中添加部分日志以及引入tests自动化测试Minidevice相关实例是否正常(测试不代表所有情况) 尝试修复部分bug
### 2023.12.2
README说明,添加[MiniDevice](./minidevice/device.py)类
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
```html
<!--[if IE]><meta http-equiv="X-UA-Compatible" content="IE=5,IE=9" ><![endif]-->
<!DOCTYPE html>
<html>
<head>
<title>minidevice</title>
<meta charset="utf-8"/>
</head>
<body><div class="mxgraph" style="max-width:100%;border:1px solid transparent;" data-mxgraph="{&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;resize&quot;:true,&quot;toolbar&quot;:&quot;zoom layers lightbox&quot;,&quot;edit&quot;:&quot;_blank&quot;,&quot;xml&quot;:&quot;&lt;mxfile host=\&quot;www.iodraw.com\&quot; modified=\&quot;2023-12-03T06:03:19.112Z\&quot; agent=\&quot;5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36\&quot; version=\&quot;13.3.6\&quot; etag=\&quot;nKgFoMgIvLT9pyJ35b5l\&quot;&gt;&lt;diagram id=\&quot;TRK5X31YmCIlcCqcmOH1\&quot; name=\&quot;第 1 页\&quot;&gt;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&lt;/diagram&gt;&lt;/mxfile&gt;&quot;}"></div>
<script type="text/javascript" src="https://www.iodraw.com/diagram/js/viewer.min.js"></script>
</body>
</html>
```
- ScreenCap
    - Minicap
    - ADBcap
    - DroidCast
- Touch
    - Minitouch
    - ADBtouch
- MiniDevice
  - ScreenCap
  - Touch
## 已知bug
- [x] ~~转发端口清理失败~~ (暂时无需清理,所有转发时都会判断端口是否被占用)
- [ ] pyminitouch库使用系统路径的adb，导致需用户自行安装adb工具并添加到环境变量中
- [ ] pyminitouch库实现存在潜在问题，主要集中在[~~连接问题~~](a1802889f30ad19db2ef12b391eff3c86b2285ea)以及输入是否合法未进行检查上面
### Tests
进行测试前请`pip install pytest`

相关使用特性见[pytest](https://pytest.org) 文档

[MiniDevice测试](tests/test_minidevice.py)

修改文件中以下参数以适配不同测试环境以及新方法
```python
SERIAL = "emulator-5554"  # 设备ID
SCREENSHOT_TIMEOUT = 500  # 截图延迟 单位ms
METHOD_LIST = [
    # 格式为 (ScreenCap,Touch)
    # 截图方法
    (Minicap, None),
    (DroidCast, None),
    (ADBcap, None),
    # 操作方法
    (None, ADBtouch),
    (None, Minitouch)
]
```
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
