from minidevicemumuapi import MuMuScreenCap
import time
m = MuMuScreenCap(0, r"C:\Program Files\Netease\MuMu Player 12")
for i in range(500):
    s = time.time()
    m.screencap_raw()
    print(time.time()-s)
# m.save_screencap()
# print(m.screencap_raw()[:20])