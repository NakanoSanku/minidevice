import time

import pytest

from minidevice import *

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


@pytest.mark.parametrize("capMethod , touchMethod", METHOD_LIST)
def test_minidevice(capMethod, touchMethod):
    # 初始化对象
    test_device = MiniDevice(SERIAL, capMethod, touchMethod, SCREENSHOT_TIMEOUT)
    if capMethod:
        # 判断截图是否可用
        assert isinstance(test_device.screenshot(), bytes)
        # 等待图片延迟结束
        time.sleep(SCREENSHOT_TIMEOUT / 1000)
        # 截图速度测试 TODO: `minicap`测试速度不准确 原因未知
        startTime = time.time()
        test_device.screenshot()
        endTime = time.time()
        logger.logger.info(f" {capMethod.__name__} 方法截图速度为{(endTime - startTime) * 1000}ms")
    if touchMethod:
        # 操作方法测试
        test_device.click(100, 100, 100)
        test_device.swipe([(10, 10), (100, 100)], 100)
    # 删除对象
    del test_device
