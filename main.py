import threading
from minidevice import MiniDevice
from minidevice.minicap import Minicap
from minidevice.minitouch import Minitouch
a=MiniDevice("emulator-5554",Minicap,Minitouch)
def increment():
    a.screenshot()
    
# 创建多个线程来并发访问共享资源
threads = []
for _ in range(10):
    t = threading.Thread(target=increment)
    threads.append(t)
    t.start()
    
# 等待所有线程完成
for t in threads:
    t.join()

