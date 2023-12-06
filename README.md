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
```
MiniDevice(self, serial=None, capMethod: Union[ADBtouch, Minicap , DroidCast] = None,
                 touchMethod: Union[ADBtouch,Minitouch] = None, screenshotTimeout=500)
```
`capMethod`|`touchMethod` 为 `ScreenCap` | `Touch` 的**子类或者子类实例**，为None时不创建对应方法

当`capMethod`|`touchMethod`包含子类时，`serial`为必须
 - screenshot_raw
 - click
 - swipe
> User无需关心具体实现过程，Developer直接继承基类即可添加新方法

### 已实现的特性
[![minidevice设计架构图.png](https://s2.loli.net/2023/12/03/Zje6Bh3TUDxbP2W.png)](https://www.iodraw.com/diagram/?lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=%E6%9C%AA%E5%91%BD%E5%90%8D%E7%BB%98%E5%9B%BE.iodraw#R7V1bd5s4EP41nNN9SA73y6PBdveS7KZNdtvuS48Ciq0NRl5ZTuL%2B%2BpUw2BARGxwT8EY%2BfUCDENXMp5lP0ogoRjB7%2BkjAfHqJIxgruho9KcZQ0XXN1HWF%2F1Oj1VriGPZaMCEoyiptBdfoB8yEaiZdogguShUpxjFF87IwxEkCQ1qSAULwY7naHY7Lb52DCRQE1yGIRekXFNHpWurqzlb%2BM0STaf5mzfbWd2Ygr5z1ZDEFEX4siIyRYgQEY7q%2Bmj0FMObKy%2FXy5ZfVl%2Fji3v7466fFv%2BBP%2F7eb3%2F86Wzc2bvLIpgsEJvTgpj9NV%2FO%2FncgjtmMNPz%2BG35BzdWZk1n0A8TJTmDKyFddVBgNlZCmer%2FgjZeQovqb4fqYHusqVu3hEsxgkrORP6SxmQo1dLiggNEMC0xS7hwn6gRMK8hrhFMXRBVjhJe8PJRDmhULdGyZmd3kDBC7QD3Ab5%2BWQV0AJJDerOcxaYOIY3MLYB%2BH9hOBlEgU4xiT9jxqqOmY%2FVqWmKjOVP0BC4VMBSJlqP0I8g5SsWJXsLnvF%2BpFsmOhuVn7cgk7TzUw4LSBOt7IBBTKkTzaNb973mY0MkExY%2F5u90K56n1p%2BHYgpJAmg0Oc6WxQxxC4Kfd2KUmQ1QJnjCii7DpnJkgDMd2Hqjpn5OrvDYQNiNEnYdciMB5llfW4fxMb6ILtB8VxAF0NjeF8Bryqw2qUa1%2FzJIgLhVY4b7ZnoEjyVKl6ABd1gNY7BfIFuN92YATJBiY8pxbOsUg3kFgaYCOLdg7s2ik3XKoHKFDGlOxWYcndAuASmxsjxRP%2F0HDAxSsGyoATfb3w8V9MdiuNckwlOK%2BUIiuEdrcDPDEVRnDY2ByFKJjccT8MzbSu5SB8cGlvJ50wNXEQwBbTgp1KzXuEFogjz9sm6rj%2FHKKGprixfsYaphNAAJ6wTzK%2Fx5iBD0CPkKKpr7s0o22%2Fu3GfYNc3bknVzl1Ww7iL1CyGYfyfgUQl0ZcDqqATSJUnYxe2KMjKxFpsquOX6Cin730xxJACDaYFugNEMCGtHUra5KdqcizB79i5OicGUwQcmFTgo29tnXQrUc4tbXg9YWduW94KhCGrmHkb2eBwEbYLEMOuBRG%2FLB7iaiBLwAL9voPIuDX%2BX%2Fto0vF3T%2Bbdn%2BBrOH0aM7WdFprwpnuAExKOt1E8DKowyg2zrXODUuXPf%2Fg%2BkdJVxALCk%2BFXRdoGXJIQ1LMGIxwTuatHLlM37uNNgBMaAoofyjOfo5vBEb32JElQ1ACWH647D6eV5gebUDPK22hZuRP8tOdy%2BMXYyHM4TVxAqOVyDEN3c5v2N2q3ZvXNa5pmC4QdDX0aDfkUDw%2BhdOLBkOKjtFsza9u5LOLDrhYPqKb2MEkeGQ%2FdRQlz6Faz8v57DZQY43hwue%2FSKo2%2Fr588M7Zmj161zr%2FBznHKT6y5mrRS3jfY27DzDyloHQkvH2jzwxFWAIcEoCnhAllSjP1TDNvtGNTRVXLKQXGPfODsZrqGpFSvDdciGpBlHRkLnNENTjXfOM7w34hmaZZ57psacu%2Bmolusax2UdHZEMTRVXM%2F6gU0gCML%2Bs3l2UVKM7quFZ%2FaMaclmjtsG3o%2B2EuMaBCxuSaxwbCj0gG877Jhsbo7XNNnSv7Odd45xzDt2wdM5B8sWVpmsapm2dq4WfWc56e3PykWfdHQgf7TD4wCdEvxauv3EkstG9Lg1zopAWVlmBM51C0B%2BPufoUITklsqAbmYKbY3dc%2Fdaw7Urw7krE3YtdzbZrgjdPOutJVoVZkeQyshXPUNyhMjIVf6h4gczA3s8JnydEW%2FmoKsQJz6iKE66%2B1y%2FVSMCuel9vErDF2fENXobTXXCSk5pXTWrM%2BosoL2zVdp98Lac09dMrjdrm7smMxhEnNGGMwvsPT4zls%2BaDaEkAV91PrJJMtl7TnSBolGzdGBSdz23yWFic5j6iOfyQaVXCQoRFELxIbY4Ei85TsTX1pPbx8%2BC7f8pr1Jw1aOrRF9hfaRBx3sCzsamkdT2jdYfmY7dG6zRN7oo3WJ88vW1xTdwWf4nZybS7djDQOY%2FTtAZETqKgHRR0T9t0cQo%2FGPqSJPSNJBycpt8eS9DF9QHJEvaOs9NhCbq4iSlZwttioHuWoIvTeskS3hgFPWAJJ3XQvoXFndxoreUznHp6pCEuGaTpkekuokyQ7B2fPPgsRnt80pCfAagfRTbj7XT4ZMWnBCWffFsMdM8nDTHRRPLJN0ZB93zSEA9TvC8%2BmRut7fxYzbJKCbFOOegf6Qiwoan9Spc1u0BTi%2Bmyd24Iw1DweuzOrWuZllqJ5delyzpaTSznxu3Lvnf%2BNcD%2BG59Ziqy%2BFguFp3hx%2B1haappjDaB7VwkaO3ThbfWnAV8JGr0maPIsor6AxhZpCU%2BWGMIHxHosJ671Jq4vAXNnyD1Ocvezb1CYqshxNLeK42itkRy34kAYJIibdaCMXGUwSj%2BdbikDU3EdntPP2C6%2FYLfGCnua3XLHiu9ICryHAtvHyK2thkdr6Kj4cDUtrJVxiNQ%2F5CEB8VpAWHrXgLDFOVG4OVvOut7gry5IOLwWDvlJx%2B7g4FZsvKXHiRdTTG%2FQDKZkYVAFC4tjwrd5IPHHijeW%2BDg6PjYHXDv0F%2FLwTasWNmoyyNbWy%2B0K%2FrjxAMoRPpB4suO64nhFk1M3B6Gh84DgiNtjLx7HeocgaHr06hAQ2J07%2FXyBZff2CaJMZ%2B8TBk2PWh0CA6%2Fu2kJzGLDi9u%2FFrdfDt391zxj9Bw%3D%3D)
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
