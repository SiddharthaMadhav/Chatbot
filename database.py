import sqlite3
from datetime import  datetime


def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_email TEXT,
                  role TEXT,
                  content TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()


def save_message(user_email, role, content):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (user_email, role, content, timestamp) VALUES (?, ?, ?, ?)',
              (user_email, role, content, datetime.now()))
    conn.commit()
    conn.close()


def load_message(user_email):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('SELECT role, content from messages WHERE user_email = (?)', (user_email, ))
    messages = [{"role": role, "content": content} for role, content in c.fetchall()]
    conn.close()
    return messages