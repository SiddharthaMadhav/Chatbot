import sqlite3
import streamlit as st
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self.conn = None

    def init_db(self):
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

    def save_message(self, email, role, content):
        try:
            conn = sqlite3.connect('chat_history.db')
            c = conn.cursor()
            c.execute('INSERT INTO messages (user_email, role, content, timestamp) VALUES (?, ?, ?, ?)',
                      (email, role, content, datetime.now()))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            st.error(f"Database error: {str(e)}")
            raise

    def load_message(self, email):
        try:
            conn = sqlite3.connect('chat_history.db')
            c = conn.cursor()
            c.execute('SELECT role, content from messages WHERE user_email = (?)', (email,))
            messages = [{"role": role, "content": content} for role, content in c.fetchall()]
            conn.close()
            return messages
        except sqlite3.Error as e:
            st.error(f"Database error: {str(e)}")
            raise
