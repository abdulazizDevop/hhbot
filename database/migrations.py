"""Database migrations and initialization"""
import sqlite3
from datetime import datetime
from config import DATABASE_PATH


def init_db():
    """Initialize database with all tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT,
            language TEXT DEFAULT 'uz',
            created_at TEXT
        )
    ''')

    # Ads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ad_type TEXT,
            status TEXT DEFAULT 'draft',
            data TEXT,
            file_id TEXT,
            file_path TEXT,
            created_at TEXT,
            updated_at TEXT,
            approved_at TEXT,
            approved_by INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (approved_by) REFERENCES users (user_id)
        )
    ''')

    # Ad history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ad_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_id INTEGER,
            action TEXT,
            old_data TEXT,
            new_data TEXT,
            field_name TEXT,
            old_value TEXT,
            new_value TEXT,
            changed_by INTEGER,
            created_at TEXT,
            FOREIGN KEY (ad_id) REFERENCES ads (id),
            FOREIGN KEY (changed_by) REFERENCES users (user_id)
        )
    ''')

    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            created_at TEXT
        )
    ''')

    # Student messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message_id INTEGER,
            group_message_id INTEGER,
            name TEXT,
            direction TEXT,
            group_number TEXT,
            message_type TEXT,
            message_text TEXT,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    # Insert default categories
    default_categories = [
        "Frontend Developer", "Backend Developer","Data Scientist",
        "Graphic Design", "IT Kids", "SMM"
    ]
    
    for category in default_categories:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (name, created_at) 
            VALUES (?, ?)
        ''', (category, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()

