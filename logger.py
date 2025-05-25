# logger.py

import sqlite3
from datetime import datetime
import config

# --- Инициализация базы данных ---
def init_db():
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            device_name TEXT,
            file_name TEXT,
            source_path TEXT,
            destination_path TEXT,
            result TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- Логирование события подключения устройства ---
def log_device_event(event_type, device_name):
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO logs (timestamp, event_type, device_name, result)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, event_type, device_name, "Success"))
    conn.commit()
    conn.close()

# --- Логирование файловой операции ---
def log_file_operation(event_type, file_name, source_path, destination_path, result):
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO logs (timestamp, event_type, file_name, source_path, destination_path, result)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, event_type, file_name, source_path, destination_path, result))
    conn.commit()
    conn.close()

# logger.py
def get_logs_by_date(date_str):
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs WHERE DATE(timestamp) = ?", (date_str,))
    logs = [
        {
            "timestamp": row[1],
            "event_type": row[2],
            "file_name": row[3],
            "src_path": row[4],
            "dst_path": row[5],
            "status": row[6]
        } for row in cursor.fetchall()
    ]
    conn.close()
    return logs
