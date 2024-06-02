import os
import platform
from adbutils import adb_path

WORK_DIR = os.path.dirname(__file__)
# connection
DEFAULT_HOST = "127.0.0.1"
PORT_SET = set(range(20000, 21000))
DEFAULT_BUFFER_SIZE = 0
DEFAULT_CHARSET = "utf-8"

# operation
DEFAULT_DELAY = 0.05

# system
# 'Linux', 'Windows' or 'Darwin'.
SYSTEM_NAME = platform.system()
NEED_SHELL = SYSTEM_NAME != "Windows"
ADB_EXECUTOR = adb_path()

# MaaTouch
MAATOUCH_FILEPATH_REMOTE = "/data/local/tmp/maatouch"
MAATOUCH_FILEPATH_LOCAL = "{}/bin/maatouch".format(WORK_DIR)

# MINICAP
MINICAP_PATH = "{}/bin/minicap/libs".format(WORK_DIR)
MINICAPSO_PATH = "{}/bin/minicap/jni".format(WORK_DIR)
MNC_HOME = "/data/local/tmp/minicap"
MNC_SO_HOME = "/data/local/tmp/minicap.so"
MINICAP_COMMAND = ["LD_LIBRARY_PATH=/data/local/tmp", "/data/local/tmp/minicap"]
MINICAP_START_TIMEOUT = 3


# DroidCast
DROIDCAST_APK_VERSION = "1.3.1"
DROIDCAST_APK_NAME_PREFIX = "DroidCast_"
DROIDCAST_APK_PATH = "{}/bin/{}{}.apk".format(WORK_DIR, DROIDCAST_APK_NAME_PREFIX,DROIDCAST_APK_VERSION)
DROIDCAST_APK_ANDROID_PATH = "/data/local/tmp/{}{}.apk".format(DROIDCAST_APK_NAME_PREFIX,DROIDCAST_APK_VERSION)

# MiniTouch
MINITOUCH_PATH = "{}/bin/minitouch/libs".format(WORK_DIR)
MINITOUCH_REMOTE_PATH = "/data/local/tmp/minitouch"
MINITOUCH_REMOTE_ADDR = "localabstract:minitouch"
MINITOUCH_SERVER_START_DELAY = 1
