
import sqlite3, os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, branch_name TEXT)")
branches = ["Jacob Main", "Jacob Annex", "Concepcion", "Legazpi", "Daet", "Pili Main", "Pili Annex", "Diversion", "Tabuc Main", "Tabuc Annex"]
for b in branches:
    uname = b.lower().replace(" ", "_")
    cur.execute("SELECT id FROM users WHERE username=?", (uname,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO users (username, password, role, branch_name) VALUES (?, ?, ?, ?)", (uname, "pass123", "branch", b))
# admin
cur.execute("SELECT id FROM users WHERE username='admin'")
if cur.fetchone() is None:
    cur.execute("INSERT INTO users (username, password, role, branch_name) VALUES (?, ?, ?, ?)", ("admin", "admin123", "admin", None))
conn.commit()
conn.close()
print("Seeded users.")
