import sqlite3
import config

conn = sqlite3.connect(config.DATABASE_PATH)
cursor = conn.cursor()

for row in cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC"):
    print(row)

conn.close()
