import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from logger import get_logs_by_date
import generator
import datetime
import os

current_password = ""
notifications_enabled = True

def update_usb_label(device_name):
    usb_device_label.config(text=f"Устройство: {device_name}")

def export_report():
    date_str = date_entry.get()
    if not date_str:
        date_str = datetime.date.today().strftime("%Y-%m-%d")

    path = filedialog.asksaveasfilename(defaultextension=".docx")
    if not path:
        return

    generator.generate_report(date_str, path)
    messagebox.showinfo("Готово", "Отчёт сохранён.")

def toggle_notifications():
    global notifications_enabled
    notifications_enabled = not notifications_enabled
    notify_btn.config(text=f"Уведомления: {'Вкл' if notifications_enabled else 'Выкл'}")


def update_log_display():
    date_str = date_entry.get()
    if not date_str:
        date_str = datetime.date.today().strftime("%Y-%m-%d")

    logs = get_logs_by_date(date_str)
    log_text.delete('1.0', tk.END)

    for log in reversed(logs):
        line = f"[{log['timestamp']}] {log['event_type']} | {log.get('file_name') or '—'} | {log.get('src_path') or '—'} → {log.get('dst_path') or '—'} | {log.get('status') or '—'}\n"

        event_type = (log.get('event_type') or "").lower()
        if "protected" in event_type:
            log_text.insert(tk.END, line, "protected")
        elif "allowed" in event_type:
            log_text.insert(tk.END, line, "ok")
        elif "blocked" in event_type:
            log_text.insert(tk.END, line, "blocked")
        elif "modified" in event_type:
            log_text.insert(tk.END, line, "modified")
        else:
            log_text.insert(tk.END, line)


def auto_refresh():
    update_log_display()
    root.after(2000, auto_refresh)  # каждые 5 секунд


def start_gui():
    global root, date_entry, notify_btn, password_entry, log_text


    root = tk.Tk()
    root.title("USB Мониторинг")

    global usb_device_label
    usb_device_label = tk.Label(root, text="Устройство: [не подключено]")
    usb_device_label.grid(row=0, column=0, columnspan=3, pady=(5, 0))

    tk.Label(root, text="Дата (ГГГГ-ММ-ДД):").grid(row=1, column=0, sticky="e")
    date_entry = tk.Entry(root)
    date_entry.grid(row=1, column=1)
    date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

    tk.Button(root, text="Получить отчёт", command=export_report).grid(row=1, column=2)

    tk.Label(root, text="Логи за дату:").grid(row=3, column=0, sticky="w", pady=(10, 0))
    log_text = scrolledtext.ScrolledText(root, width=100, height=20)
    log_text.tag_config("ok", foreground="green")
    log_text.tag_config("blocked", foreground="red")
    log_text.tag_config("modified", foreground="orange")
    log_text.tag_config("protected", foreground="red")

    log_text.grid(row=4, column=0, columnspan=3)

    tk.Button(root, text="Обновить логи", command=update_log_display).grid(row=5, column=2, pady=5)

    update_log_display()
    auto_refresh()
    root.mainloop()
