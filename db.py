import sqlite3


def get_connection():
    return sqlite3.connect("bot.db")


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER,
        name TEXT,
        phone TEXT,
        reminder_send INTEGER DEFAULT 0           
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 
    )
    """)

    conn.commit()
    conn.close()


def add_lead(tg_id: int, name: str, phone: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO leads (tg_id, name, phone) VALUES (?, ?, ?)",
        (tg_id, name, phone)
    )
 
    conn.commit()
    conn.close()


def get_leads():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM leads")
    rows = cursor.fetchall()

    conn.close()
    return rows

def get_leads_for_reminder():
    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
    SELECT id, tg_id FROM leads
    WHERE reminder_sent = 0               
""")
    rows = cursor.fetchall()
    conn.close()
    return rows


def mark_reminder_sent(lead_id: int):
    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
    UPDATE leads SET reminder_sent = 1 WHERE id = ?,
                   (lead_id)
""")
    conn.commit()
    conn.close()