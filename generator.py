import logger

def generate_report(date_str, save_path):
    logs = logger.get_logs_by_date(date_str)
    with open(save_path, "w", encoding="utf-8") as file:
        file.write(f"Отчёт за {date_str}\n")
        file.write("=" * 40 + "\n")
        for log in logs:
            line = f"[{log['timestamp']}] {log['event_type']} | {log['file_name']} | {log['src_path']} → {log['dst_path']} ({log['status']})\n"
            file.write(line)
