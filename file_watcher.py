import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logger
import config
from collections import defaultdict
import hashlib
import protector


usb_hash_cache = {} #последний хеш
USB_DRIVES = ["E:\\", "F:\\", "G:\\"]
IGNORE_PATHS = ["AppData", "ProgramData", "Windows", "JetBrains", "System32", "Edge", "$Recycle.Bin"]

# Кэш недавно созданных файлов на ПК: {file_name: (size, path, timestamp)}
pc_file_hash_cache = defaultdict(lambda: ("", 0.0))  # {hash: (path, timestamp)}\последний хеш
usb_to_pc_hashes = dict()  # {abs_path: hash}|путь

def get_partial_hash(path, block_size=1024 * 1024):
    try:
        with open(path, 'rb') as f:
            data = f.read(block_size)
            return hashlib.sha256(data).hexdigest()
    except Exception:
        return None

def get_file_hash(path):
    try:
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def is_usb_path(path):
    for drive in USB_DRIVES:
        if path.upper().startswith(drive.upper()):
            return True
    return False

def is_protected_path(path):
    for protected in config.PROTECTED_DIRECTORIES:
        if path.lower().startswith(protected.lower()):
            return True
    return False

def is_ignored_path(path):
    return any(ignored.lower() in path.lower() for ignored in IGNORE_PATHS)

def find_matching_file_on_usb(file_name, size_bytes):
    for drive in USB_DRIVES:
        for root, _, files in os.walk(drive):
            for f in files:
                if f == file_name:
                    usb_path = os.path.join(root, f)
                    try:
                        if os.path.getsize(usb_path) == size_bytes:
                            return usb_path
                    except:
                        continue
    return None

class FileEventHandler(FileSystemEventHandler):
    def on_moved(self, event):
        if event.is_directory:
            return
        self.process_move(event.src_path, event.dest_path)


    def on_modified(self, event):
        if event.is_directory:
            return

        path = os.path.abspath(event.src_path)
        if is_ignored_path(path):
            return

        file_hash = get_file_hash(path)
        if not file_hash:
            return

        if file_hash in usb_hash_cache:
            return  # всё в порядке, файл известен

        print(f"[MODIFIED] Файл был изменён после копирования с флешки: {path}")
        logger.log_file_operation("Modified After USB Copy", os.path.basename(path), "USB", path, "Modified")

    def on_created(self, event):
        if not event.is_directory:
            self.process_created(event.src_path)

    def process_move(self, src, dst):
        src = os.path.abspath(src)
        dst = os.path.abspath(dst)
        file_name = os.path.basename(src)
        ext = os.path.splitext(file_name)[1].lower()

        if is_ignored_path(src) or is_ignored_path(dst):
            return

        if is_protected_path(src):
            print(f"[BLOCKED] Копирование из защищённой директории: {src} -> {dst}")
            logger.log_file_operation("Blocked Protected Folder", file_name, src, dst, "Blocked")
            return

        if is_usb_path(src) and not is_usb_path(dst) and ext in config.FORBIDDEN_EXTENSIONS:
            print(f"[BLOCKED] Опасный файл с флешки: {file_name} -> {dst}")
            protector.protect_file(dst)  # ← Защита: удалит файл, если не введён пароль
            logger.log_file_operation("Blocked Dangerous From USB", file_name, src, dst, "Blocked")
            return

        if is_usb_path(src) and not is_usb_path(dst):
            direction = "USB -> ПК"
        elif not is_usb_path(src) and is_usb_path(dst):
            direction = "ПК -> USB"
        elif is_usb_path(src) and is_usb_path(dst):
            direction = "На флешке"
        else:
            direction = "Локально"
        # ⚠️ Проверка: переименование разрешённого файла в опасное расширение
        if not is_usb_path(src) and not is_usb_path(dst):
            old_ext = os.path.splitext(src)[1].lower()
            new_ext = os.path.splitext(dst)[1].lower()

            if old_ext not in config.FORBIDDEN_EXTENSIONS and new_ext in config.FORBIDDEN_EXTENSIONS:
                from protector import protect_file
                print(f"[WARN] Попытка изменить расширение с безопасного на опасное: {src} -> {dst}")
                protect_file(dst)
                return

        print(f"[OK] {direction}: {file_name}\n     из {src}\n     в {dst}")
        logger.log_file_operation("File Moved", file_name, src, dst, "Allowed")

    def process_created(self, path):
        path = os.path.abspath(path)
        file_name = os.path.basename(path)
        ext = os.path.splitext(file_name)[1].lower()

        if is_ignored_path(path):
            return

        try:
            file_size = os.path.getsize(path)
        except:
            return

        now = time.time()

        if not is_usb_path(path):
            hash_value = get_partial_hash(path)
            if hash_value:
                pc_file_hash_cache[hash_value] = (path, now)

        hash_value = get_partial_hash(path)
        if hash_value and hash_value in pc_file_hash_cache:
            src_path, cached_time = pc_file_hash_cache[hash_value]
            if now - cached_time <= 10:  # до 10 секунд — допустимое окно
                print(f"[GUESS] Файл скопирован с ПК -> флешку (по хешу): {file_name}\n       из {src_path} -> {path}")
                logger.log_file_operation("Smart Guess PC to USB (Hash)", file_name, src_path, path, "Allowed")
        match = find_matching_file_on_usb(file_name, file_size)
        if match:
            if ext in config.FORBIDDEN_EXTENSIONS:
                print(f"[BLOCKED] Найден двойник на флешке — файл скопирован: {file_name} -> {path}")
                logger.log_file_operation("Smart Match From USB", file_name, match, path, "Blocked")
                from protector import protect_file
                protect_file(path)
            else:
                print(f"[OK] Разрешённый файл с флешки: {file_name} -> {path}")
                logger.log_file_operation("Allowed File From USB", file_name, match, path, "Allowed")

        file_hash = get_file_hash(path)
        if file_hash:
            usb_hash_cache[file_hash] = path

        hash_value = get_partial_hash(path)
        if hash_value:
            usb_to_pc_hashes[path] = hash_value


def start_watching(path_to_watch):
    event_handler = FileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()
    print(f"[INFO] Мониторинг файлов запущен в: {path_to_watch}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
