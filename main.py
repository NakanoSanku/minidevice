import time
from minidevice import DriodCast
a=DriodCast("127.0.0.1:16384")
for i in range(10):
    s=time.time()
    a.screencap_opencv()
    print(time.time()-s)