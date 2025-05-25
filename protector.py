import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import simpledialog, messagebox
import logger
load_dotenv()
SECURITY_PASSWORD = os.getenv("SECURITY_PASSWORD", "1234")

def ask_password_gui():
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        root.update()  # важно для корректной инициализации перед вызовом диалога

        entered = simpledialog.askstring(
            "Подтверждение",
            "Введите пароль для разрешения опасного действия:",
            show="*",
            parent=root
        )
        root.destroy()

        return entered == SECURITY_PASSWORD if entered is not None else False

    except Exception as e:
        print(f"[GUI ERROR] Ошибка при запросе пароля: {e}")
        return False
def protect_file(file_path):
    if not ask_password_gui():
        try:
            os.remove(file_path)
            print(f"[PROTECTED] Файл {file_path} удалён из-за неверного пароля.")
            logger.log_file_operation("Protected Deletion", os.path.basename(file_path), "Unknown", file_path,
                                      "Blocked")

        except Exception as e:
            print(f"[ERROR] Не удалось удалить файл {file_path}: {e}")
    else:
        print(f"[ACCESS GRANTED] Файл {file_path} сохранён.")
