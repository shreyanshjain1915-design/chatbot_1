import sqlite3

conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
id INTEGER PRIMARY KEY AUTOINCREMENT,
session_id TEXT,
role TEXT,
message TEXT
)
""")

conn.commit()


def save_message(session_id, role, message):
    cursor.execute(
        "INSERT INTO chats (session_id, role, message) VALUES (?,?,?)",
        (session_id, role, message),
    )
    conn.commit()


def get_history(session_id):
    cursor.execute(
        "SELECT role, message FROM chats WHERE session_id=?",
        (session_id,),
    )
    rows = cursor.fetchall()

    return [{"role": r[0], "content": r[1]} for r in rows]