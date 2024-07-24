from minidevice import MiniCap
import time
m= MiniCap("127.0.0.1:16384",skip_frame=True)

for i in range(10):
    s = time.time()
    m.screencap_raw()
    print(f"{(time.time()-s)*1000}ms")
time.sleep(1)

s = time.time()
m.screencap_raw()
print(f"{(time.time()-s)*1000}ms")
