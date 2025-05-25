# --- Запрещённые расширения файлов ---
FORBIDDEN_EXTENSIONS = [
    ".exe", ".apk", ".bat", ".cmd", ".ps1", ".js", ".vbs", ".msi", ".com"
]

# --- Защищённые директории ---
PROTECTED_DIRECTORIES = [
    "D:\\Secret"
]

# --- Настройки уведомлений ---
ADMIN_EMAIL = "admin@example.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_username"
SMTP_PASSWORD = "your_password"

# --- Пути для базы данных и логов ---
DATABASE_PATH = "device_log.db"
LOG_FILE_PATH = "device_log.txt"

# --- Прочие настройки ---
NOTIFY_USER = True       # Показывать ли пользователю всплывающее сообщение при нарушении
SEND_ADMIN_ALERTS = True # Отправлять ли админу уведомления по email

# config.py
ADMIN_NOTIFY = True
MONITORED_PATH = "C:\\Users\\ulamu"
