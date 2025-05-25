import threading
import logger
import device_monitor
import file_watcher
import time
import os
from gui import start_gui
import sys

def background_monitoring():
    print("Запуск системы мониторинга флешек...")
    logger.init_db()
    print("База данных инициализирована.")

    threading.Thread(target=device_monitor.start_monitoring, daemon=True).start()
    print("Мониторинг устройств запущен.")

    home_dir = os.path.expanduser("~")
    threading.Thread(target=file_watcher.start_watching, args=(home_dir,), daemon=True).start()


    print("Ожидание подключения/отключения устройств...")

if __name__ == "__main__":
    background_monitoring()

    threading.Thread(target=start_gui, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Остановка по Ctrl+C")
