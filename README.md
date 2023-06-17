# minidevice v2
重构代码,添加DroidCast截图方法
## minicap/minitouch一键配置
### 源码
[sh脚本](script.sh)
### 使用方法
```sh
 adb -s ${设备id} shell "curl -o /sdcard/script.sh https://raw.githubusercontent.com/NakanoSanku/minidevice/master/script.sh && sh /sdcard/script.sh"
```
[跳转API文档](https://nakanosanku.github.io/minidevice)

    粗略地写了一些其他功能，并使用mkdoc自动生成了文档,后续会继续完善(~~画饼~~)

|模块|描述|完成情况|
|----|----|------|
|adb|adb操作设备|✅|
|images|图色相关|✅|
|touch|基础操作|✅|
|screencap|截图|✅|

- ✅代表大部分功能已实现
- ❌代表完成度很低(局限性较大)
- 没写出来的就是基本还没写的

[English README](README_en.md)

一个对安卓设备(主要是安卓模拟器)进行基础操作的工具包

由于部分没有基础，故whl中为用户提供adb工具,minicap/minitouch等静态资源

以方便网络环境较差的用户能够正常使用

由于uiautomator截图严重拉高模拟器cpu占用

加上uiautomator已许久未更新,移除这一方法
## requirements
`opencv-python` [`pyminitouch`](https://github.com/williamfzc/pyminitouch)
## 使用实例
采用抽象类定义截图基类

所以DroidCast,Minicap,ADBcap使用方法一模一样
```python
from minidevice import Minicap
#创建截图对象
capdevice = Minicap("127.0.0.1:16834")
#截图
cap = capdevice.screen_opencv()
#截图并保存本地
capdevice.save_screen()
```
当然minitouh,ADBtouch使用方法一模一样
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
图像识别函数使用方法见[文档](https://nakanosanku.github.io/minidevice/images)