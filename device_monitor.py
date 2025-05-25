# device_monitor.py

import pythoncom
import win32com.client
import threading
import logger
import file_watcher
from gui import update_usb_label

class DeviceEventHandler:
    def __init__(self):
        self.wmi = win32com.client.GetObject("winmgmts:")

    def monitor_usb_events(self):
        query_insert = "SELECT * FROM __InstanceCreationEvent WITHIN 2 WHERE TargetInstance ISA 'Win32_USBHub'"
        query_remove = "SELECT * FROM __InstanceDeletionEvent WITHIN 2 WHERE TargetInstance ISA 'Win32_USBHub'"

        watcher_insert = self.wmi.ExecNotificationQuery(query_insert)
        watcher_remove = self.wmi.ExecNotificationQuery(query_remove)

        print("Ожидание подключения/отключения устройств...")

        while True:
            try:
                event = watcher_insert.NextEvent(1000)
                if event:
                    device_name = event.TargetInstance.Name
                    print(f"[+] Устройство подключено: {device_name}")
                    update_usb_label(device_name)
                    logger.log_device_event("Device Connected", device_name)

                    drive_letter = self.get_usb_drive_letter()
                    if drive_letter:
                        print(f"[INFO] USB диск подключён как: {drive_letter}")
                        file_watcher.start_watching(drive_letter)
            except:
                pass

            try:
                event = watcher_remove.NextEvent(1000)
                if event:
                    device_name = event.TargetInstance.Name
                    print(f"[-] Устройство отключено: {device_name}")
                    update_usb_label("[не подключено]")
                    logger.log_device_event("Device Disconnected", device_name)
            except:
                pass

    def get_usb_drive_letter(self):
        for disk in self.wmi.InstancesOf("Win32_LogicalDisk"):
            if disk.DriveType == 2:  # 2 = Removable Disk
                return disk.DeviceID + "\\"
        return None

def start_monitoring():
    def monitor():
        pythoncom.CoInitialize()
        handler = DeviceEventHandler()
        handler.monitor_usb_events()

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
