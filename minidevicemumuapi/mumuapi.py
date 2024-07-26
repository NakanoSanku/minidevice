import ctypes


class MuMuApi:
    def __init__(self, dllPath):
        self.nemu = ctypes.CDLL(dllPath)
        # 定义返回类型和参数类型
        self.nemu.nemu_connect.restype = ctypes.c_int
        self.nemu.nemu_connect.argtypes = [ctypes.c_wchar_p, ctypes.c_int]

        self.nemu.nemu_disconnect.argtypes = [ctypes.c_int]

        self.nemu.nemu_capture_display.restype = ctypes.c_int
        self.nemu.nemu_capture_display.argtypes = [
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_ubyte),
        ]

        self.nemu.nemu_input_text.restype = ctypes.c_int
        self.nemu.nemu_input_text.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_char_p,
        ]

        self.nemu.nemu_input_event_touch_down.restype = ctypes.c_int
        self.nemu.nemu_input_event_touch_down.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]

        self.nemu.nemu_input_event_touch_up.restype = ctypes.c_int
        self.nemu.nemu_input_event_touch_up.argtypes = [
            ctypes.c_int, ctypes.c_int]

        self.nemu.nemu_input_event_key_down.restype = ctypes.c_int
        self.nemu.nemu_input_event_key_down.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]

        self.nemu.nemu_input_event_key_up.restype = ctypes.c_int
        self.nemu.nemu_input_event_key_up.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]

    def connect(self, emulatorInstallPath, instanceIndex):
        return self.nemu.nemu_connect(emulatorInstallPath, instanceIndex)

    def disconnect(self, handle):
        return self.nemu.nemu_disconnect(handle)

    def captureDisplay(self, handle, displayId, bufferSize, width, height, pixels):
        return self.nemu.nemu_capture_display(
            handle, displayId, bufferSize, width, height, pixels
        )

    def inputText(self, handle, size, buf):
        return self.nemu.nemu_input_text(handle, size, buf)

    def inputEventTouchDown(self, handle, displayId, xPoint, yPoint):
        return self.nemu.nemu_input_event_touch_down(handle, displayId, xPoint, yPoint)

    def inputEventTouchUp(self, handle, displayId):
        return self.nemu.nemu_input_event_touch_up(handle, displayId)

    def inputEventKeyDown(self, handle, displayId, keyCode):
        return self.nemu.nemu_input_event_key_down(handle, displayId, keyCode)

    def inputEventKeyUp(self, handle, displayId, keyCode):
        return self.nemu.nemu_input_event_key_up(handle, displayId, keyCode)
