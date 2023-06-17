import shutil
import subprocess
import random
from minidevice.logger import logger


from minidevice.screencap import ScreenCap
from minidevice.touch import Touch

ADB_PATH = "adb"
if shutil.which("adb.exe") is None:
    import os

    WORK_DIR = os.path.dirname(__file__)
    ADB_PATH = shutil.which("adb.exe", path="{}/bin".format(WORK_DIR))


class ADB:
    def __init__(self, device=None):
        self.device = device

    def adb_command(self, command: list):
        """执行shell脚本语句,获取返回的源数据"""
        adb_command = [ADB_PATH]
        if self.device:
            adb_command.extend(["-s", self.device])
        adb_command.extend(command)
        try:
            process = subprocess.Popen(
                adb_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            data, err = process.communicate(timeout=10)
            if process.returncode == 0:
                return data
            else:
                logger.error("ADB命令执行失败\n报错信息:{}".format(err))
        except FileNotFoundError:
            logger.error("ADB不存在或无法执行")
        except subprocess.TimeoutExpired:
            logger.error("ADB命令执行超时")

    def _run_adb_command(self, command: list):
        adb_command = [ADB_PATH]
        if self.device:
            adb_command.extend(["-s", self.device])
        adb_command.extend(command)
        try:
            result = subprocess.run(adb_command, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("\nADB命令执行失败\n报错信息:{}".format(result.stderr))
            return result.stdout
        except subprocess.CalledProcessError as e:
            # 执行失败，处理异常情况
            logger.error(f"命令执行失败\n返回码:, {e.returncode}\n标准错误:{e.stderr}")
        except subprocess.TimeoutExpired as e:
            # 命令执行超时，处理超时情况
            logger.error("命令执行超时")

    def forward_port(self, server, port=None) -> int:
        while True:
            localport = random.randint(11111, 20000) if port is None else port
            local = "tcp:{}".format(localport)
            result = self._run_adb_command(["forward", local, server])
            if result.split(":")[-1] != "":
                return int(result.split(":")[-1])
            else:
                if port is not None:
                    self.remove_forward(port)

    def remove_forward(self, port):
        self._run_adb_command(["forward", "--remove", "tcp:{}".format(port)])

    @staticmethod
    def list_forward_port():
        output = subprocess.run(
            [ADB_PATH, "forward", "--list"], capture_output=True, text=True
        )
        list_port = output.stdout.split("\n")[:-2]
        return list_port

    def get_version(self):
        output = self._run_adb_command(["version"])
        return output.strip()

    def start_server(self):
        self._run_adb_command(["start-server"])

    def stop_server(self):
        self._run_adb_command(["kill-server"])

    def enable_root(self):
        self._run_adb_command(["root"])

    def set_port(self, port):
        self._run_adb_command(["tcpip", str(port)])

    def clean_forward(self):
        self._run_adb_command(["forward", "--remove-all"])

    @staticmethod
    def list_devices():
        output = ADB._run_adb_command(ADB(), ["devices"])
        devices = output.split("\n")[1:]
        devices = [device.split("\t")[0] for device in devices if device.strip()]
        return devices

    @staticmethod
    def list_devices_info():
        output = ADB._run_adb_command(ADB(), ["devices", "-l"])
        devices = output.split("\n")[1:]
        devices = [device.split("\t")[0] for device in devices if device.strip()]
        status = [device.split("\t")[1] for device in devices if device.strip()]
        remark = [device.split("\t")[2] for device in devices if device.strip()]
        return list(zip(devices, status, remark))

    def install_apk(self, apk_path):
        self._run_adb_command(["install", apk_path])

    def uninstall_app(self, package_name, save_data=False):
        adb_command = (
            ["uninstall", "-k", package_name]
            if save_data
            else ["uninstall", package_name]
        )
        self._run_adb_command(adb_command)

    def clear_app_data(self, package_name):
        self._run_adb_command(["shell", "pm", "clear", package_name])

    def list_apps(self, system=False, third_party=False, package_name_contains=None):
        command = ["shell", "pm", "list", "packages"]
        if system:
            command.append("-s")
        if third_party:
            command.append("-3")
        output = self._run_adb_command(command).strip()
        packages = output.split("\n")
        if package_name_contains:
            packages = [
                package for package in packages if package_name_contains in package
            ]
        packages = [package.split(":")[-1] for package in packages]
        return packages

    def get_foreground_activity(self):
        output = self._run_adb_command(
            [
                "shell",
                "dumpsys",
                "activity",
                "activities",
                "|",
                "grep",
                "mResumedActivity",
            ]
        )
        return output.strip()

    def get_running_services(self):
        output = self._run_adb_command(["shell", "dumpsys", "activity", "services"])
        return output.strip()

    def get_app_info(self, package_name):
        output = self._run_adb_command(["shell", "dumpsys", "package", package_name])
        return output.strip()

    def get_app_install_path(self, package_name):
        output = self._run_adb_command(["shell", "pm", "path", package_name])
        return output.strip()

    def start_app(self, package_name, activity_name):
        self._run_adb_command(
            ["shell", "am", "start", "-n", f"{package_name}/{activity_name}"]
        )

    def start_service(self, package_name, service_name):
        self._run_adb_command(
            ["shell", "am", "startservice", f"{package_name}/{service_name}"]
        )

    def stop_service(self, package_name, service_name):
        self._run_adb_command(
            ["shell", "am", "stopservice", f"{package_name}/{service_name}"]
        )

    def send_broadcast(self, action):
        self._run_adb_command(["shell", "am", "broadcast", "-a", action])

    def force_stop_app(self, package_name):
        self._run_adb_command(["shell", "am", "force-stop", package_name])

    def trim_memory(self):
        self._run_adb_command(
            ["shell", "am", "send-trim-memory", "org.example.package", "HIDDEN"]
        )

    def pull_file(self, device_path, local_path):
        self._run_adb_command(["pull", device_path, local_path])

    def push_file(self, local_path, device_path):
        self._run_adb_command(["push", local_path, device_path])

    def press_power_button(self):
        self._run_adb_command(["shell", "input", "keyevent", "26"])

    def press_menu_button(self):
        self._run_adb_command(["shell", "input", "keyevent", "82"])

    def press_home_button(self):
        self._run_adb_command(["shell", "input", "keyevent", "3"])

    def press_back_button(self):
        self._run_adb_command(["shell", "input", "keyevent", "4"])

    def control_volume(self, direction):
        if direction == "up":
            self._run_adb_command(["shell", "input", "keyevent", "24"])
        elif direction == "down":
            self._run_adb_command(["shell", "input", "keyevent", "25"])

    def control_media(self, action):
        if action == "play":
            self._run_adb_command(["shell", "input", "keyevent", "85"])
        elif action == "pause":
            self._run_adb_command(["shell", "input", "keyevent", "86"])
        elif action == "next":
            self._run_adb_command(["shell", "input", "keyevent", "87"])
        elif action == "previous":
            self._run_adb_command(["shell", "input", "keyevent", "88"])

    def turn_on_screen(self):
        self._run_adb_command(["shell", "input", "keyevent", "224"])

    def turn_off_screen(self):
        self._run_adb_command(["shell", "input", "keyevent", "223"])

    def swipe_unlock(self):
        self._run_adb_command(["shell", "input", "swipe", "100", "500", "500", "500"])

    def input_text(self, text):
        self._run_adb_command(["shell", "input", "text", text])

    def view_logcat(self):
        self._run_adb_command(["logcat"])

    def filter_logcat_by_level(self, log_level):
        self._run_adb_command(["logcat", "*:" + log_level])

    def filter_logcat_by_tag_and_level(self, tag, log_level):
        self._run_adb_command(["logcat", tag + ":" + log_level])

    def set_log_format(self, log_format):
        self._run_adb_command(["logcat", "-v", log_format])

    def clear_logcat(self):
        self._run_adb_command(["logcat", "-c"])

    def view_kernel_log(self):
        self._run_adb_command(["shell", "dmesg"])

    def get_device_model(self):
        output = self._run_adb_command(["shell", "getprop", "ro.product.model"])
        return output.strip()

    def get_battery_status(self):
        output = self._run_adb_command(["shell", "dumpsys", "battery"])
        return str_to_dict(output.strip())

    def get_screen_resolution(self):
        output = self._run_adb_command(["shell", "wm", "size"])
        return str_to_dict(output.strip())["Physical size"]

    def get_screen_density(self):
        output = self._run_adb_command(["shell", "wm", "density"])
        return str_to_dict(output.strip())["Physical density"]

    def get_display_info(self):
        output = self._run_adb_command(["shell", "dumpsys", "display"])
        return str_to_dict(output.strip())

    def get_android_id(self):
        output = self._run_adb_command(
            ["shell", "settings", "get", "secure", "android_id"]
        )
        return output.strip()

    def get_imei(self):
        output = self._run_adb_command(
            ["shell", "service", "call", "iphonesubinfo", "1"]
        )
        return output.strip()

    def get_android_version(self):
        output = self._run_adb_command(["shell", "getprop", "ro.build.version.release"])
        return output.strip()

    def get_ip_address(self):
        output = self._run_adb_command(["shell", "ifconfig", "wlan0"])
        return output.strip()

    def get_mac_address(self):
        output = self._run_adb_command(["shell", "cat", "/sys/class/net/wlan0/address"])
        return output.strip()

    def get_cpu_info(self):
        output = self._run_adb_command(["shell", "cat", "/proc/cpuinfo"])
        return str_to_dict(output.strip())

    def get_memory_info(self):
        output = self._run_adb_command(["shell", "cat", "/proc/meminfo"])
        return str_to_dict(output.strip())

    def print_build_prop(self):
        output = self._run_adb_command(["shell", "cat", "/system/build.prop"])
        return output.strip()

    def get_sdk(self):
        output = self._run_adb_command(["shell", "getprop", "ro.build.version.sdk"])
        return int(output.strip())

    def get_security_patch(self):
        output = self._run_adb_command(
            ["shell", "getprop", "ro.build.version.security_patch"]
        )
        return output.strip()

    def get_product_brand(self):
        output = self._run_adb_command(["shell", "getprop", "ro.product.brand"])
        return output.strip()

    def get_product_name(self):
        output = self._run_adb_command(["shell", "getprop", "ro.product.name"])
        return output.strip()

    def get_product_board(self):
        output = self._run_adb_command(["shell", "getprop", "ro.product.board"])
        return output.strip()

    def get_product_cpu_abilist(self):
        output = self._run_adb_command(["shell", "getprop", "ro.product.cpu.abilist"])
        return output.strip()

    def get_abi(self):
        output = self._run_adb_command(["shell", "getprop", "ro.product.cpu.abi"])
        return output.strip()

    def get_isUsbOtgEnabled(self):
        output = self._run_adb_command(
            ["shell", "getprop", "persist.sys.isUsbOtgEnabled"]
        )
        return output.strip()

    def get_heapsize(self):
        output = self._run_adb_command(["shell", "getprop", "dalvik.vm.heapsize"])
        return output.strip()

    def get_lcd_density(self):
        output = self._run_adb_command(["shell", "getprop", "ro.sf.lcd_density"])
        return output.strip()

    def set_resolution(self, width, height):
        self._run_adb_command(["shell", "wm", "size", f"{width}x{height}"])

    def set_density(self, density):
        self._run_adb_command(["shell", "wm", "density", str(density)])

    def set_display_area(self, left, top, right, bottom):
        self._run_adb_command(
            ["shell", "wm", "overscan", f"{left},{top},{right},{bottom}"]
        )

    def disable_usb_debugging(self):
        self._run_adb_command(
            ["shell", "settings", "put", "global", "adb_enabled", "0"]
        )

    def allow_non_sdk_api(self):
        self._run_adb_command(
            ["shell", "settings", "put", "global", "hidden_api_policy", "1"]
        )

    def disable_non_sdk_api(self):
        self._run_adb_command(
            ["shell", "settings", "put", "global", "hidden_api_policy", "0"]
        )

    def hide_status_bar(self):
        self._run_adb_command(
            [
                "shell",
                "settings",
                "put",
                "global",
                "policy_control",
                "immersive.status=*",
            ]
        )

    def show_status_bar(self):
        self._run_adb_command(
            ["shell", "settings", "put", "global", "policy_control", "null"]
        )

    def hide_navigation_bar(self):
        self._run_adb_command(
            [
                "shell",
                "settings",
                "put",
                "global",
                "policy_control",
                "immersive.navigation=*",
            ]
        )

    def show_navigation_bar(self):
        self._run_adb_command(
            ["shell", "settings", "put", "global", "policy_control", "null"]
        )

    def take_screenshot(self, file_path):
        self._run_adb_command(["exec-out", "screencap", "-p", ">", file_path])

    def start_screen_recording(self, file_path):
        self._run_adb_command(["shell", "screenrecord", file_path])

    def remount_system_partition(self):
        self._run_adb_command(["shell", "mount", "-o", "remount,rw", "/system"])

    def get_wifi_password(self, ssid):
        output = self._run_adb_command(
            [
                "shell",
                "su",
                "-c",
                f'cat /data/misc/wifi/wpa_supplicant.conf | grep -A 4 "ssid=\\"{ssid}\\""',
            ]
        )
        return output.strip()

    def set_date_time(self, date_time):
        self._run_adb_command(["shell", "su", "-c", f'date -s "{date_time}"'])

    def reboot_device(self):
        self._run_adb_command(["shell", "su", "-c", "reboot"])

    def check_root_status(self):
        output = self._run_adb_command(["shell", "su", "-c", "id"])
        if "root" in output.strip():
            return True
        else:
            return False

    def enable_monkey_stress_test(self):
        self._run_adb_command(["shell", "settings", "put", "global", "monkey", "0"])

    def disable_monkey_stress_test(self):
        self._run_adb_command(["shell", "settings", "put", "global", "monkey", "1"])

    def enable_wifi(self):
        self._run_adb_command(["shell", "svc", "wifi", "enable"])

    def disable_wifi(self):
        self._run_adb_command(["shell", "svc", "wifi", "disable"])

    def reboot_recovery(self):
        self._run_adb_command(["reboot", "recovery"])

    def reboot_android(self):
        self._run_adb_command(["reboot"])

    def reboot_fastboot(self):
        self._run_adb_command(["reboot", "bootloader"])

    def sideload_update(self, update_zip_path):
        self._run_adb_command(["sideload", update_zip_path])

    def enable_selinux(self):
        self._run_adb_command(["shell", "setenforce", "1"])

    def disable_selinux(self):
        self._run_adb_command(["shell", "setenforce", "0"])

    def enable_dm_verity(self):
        self._run_adb_command(
            ["shell", "su", "-c", "setprop", "verity.mode", "enforcing"]
        )

    def disable_dm_verity(self):
        self._run_adb_command(
            ["shell", "su", "-c", "setprop", "verity.mode", "disabled"]
        )

    def swipe(self, start_x, start_y, end_x, end_y, duration=250):
        adb_command = ["shell", "input", "touchscreen", "swipe"]
        adb_command.extend(
            [str(start_x), str(start_y), str(end_x), str(end_y), str(duration)]
        )
        self._run_adb_command(adb_command)

    def click(self, x: int, y: int, duration=150):
        adb_command = ["shell", "input", "touchscreen", "swipe"]
        adb_command.extend([str(x), str(y), str(x), str(y), str(duration)])
        self._run_adb_command(adb_command)

    def change_file_permission(self, permission, file_path):
        self._run_adb_command(["shell", "chmod", permission, file_path])

    def check_disk_space(self):
        output = self._run_adb_command(["shell", "df"])
        return output.strip()

    def kill_process(self, pid):
        self._run_adb_command(["shell", "kill", str(pid)])

    def list_directory_contents(self, directory):
        output = self._run_adb_command(["shell", "ls", "-la", directory])
        return output.strip()

    def move_file(self, source_path, destination_path):
        self._run_adb_command(["shell", "mv", source_path, destination_path])

    def view_running_processes(self):
        output = self._run_adb_command(["shell", "ps"])
        return output.strip()

    def remove_file(self, file_path):
        self._run_adb_command(["shell", "rm", "-rf", file_path])

    def view_top_processes(self):
        output = self._run_adb_command(["shell", "top", "-n", "1"])
        return output.strip()

    def get_service_list(self):
        output = self._run_adb_command(["shell", "service", "list"])
        return output.strip()

    def get_iomem(self):
        output = self._run_adb_command(["shell", "cat", "/proc/iomem"])
        return output.strip()

    def get_procrank(self):
        output = self._run_adb_command(["shell", "procrank"])
        return output.strip()

    def screencap_raw(self):
        """获取截图源数据"""
        return self.adb_command(["exec-out", "screencap", "-p"])


def str_to_dict(str):
    dict_info = {}
    lines = str.splitlines()
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            dict_info[key.strip()] = value.strip()
    return dict_info


class ADBcap(ScreenCap, ADB):
    def __init__(self, device=None) -> None:
        ADB.__init__(self, device=device)

    def screencap_raw(self) -> bytes:
        """
        screencap_raw ADB截图

        Returns:
            图像字节流 (bytes): 
        """
        logger.debug(f"screen by ADB")
        return ADB.screencap_raw(self)



class ADBtouch(Touch, ADB):
    def __init__(self, device=None) -> None:
        ADB.__init__(self, device=device)

    def click(self, x: int, y: int, duration: int = 100):
        """
        click ADB 点击

        Args:
            x (int): 横坐标
            y (int): 纵坐标
            duration (int, optional): 持续时间. Defaults to 100.
        """
        ADB.click(self, x, y, duration)
        logger.debug(f"ADB click ({x},{y}) consume:{duration}ms")

    def swipe(self, points: list, duration: int = 300):
        """
        swipe 滑动

        Args:
            points (list): [(x,y),(x,y)] 坐标列表
            duration (int): 持续时间. Defaults to 300.
        """
        start_x, start_y = points[0]
        end_x, end_y = points[-1]
        ADB.swipe(self, start_x, start_y, end_x, end_y, duration)
        logger.debug(f"ADB swipe from ({points[0]}) to ({points[-1]}) consume:{duration}ms")