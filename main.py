from minidevice import DroidCast,ADBcap,Minicap,Minitouch
a = Minicap("24cd69af")
b = DroidCast("emulator-5554")
a.save_screencap("a.png")
b.save_screencap("b.png")
