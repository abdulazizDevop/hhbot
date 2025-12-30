# database/db.py
import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT, -- 'graduate' or 'employer'
            language TEXT DEFAULT 'uz',
            created_at TEXT
        )
    ''')

    # Ads table - yangilangan struktura
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ad_type TEXT, -- 'graduate' or 'employer'
            status TEXT DEFAULT 'draft', -- 'draft', 'pending', 'approved', 'rejected', 'cancelled'
            data TEXT, -- JSON with ad content
            file_id TEXT, -- Telegram file_id for resume
            file_path TEXT, -- Local file path (optional)
            created_at TEXT,
            updated_at TEXT,
            approved_at TEXT,
            approved_by INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (approved_by) REFERENCES users (user_id)
        )
    ''')

    # Ad history - har bir o'zgarishni kuzatish uchun
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ad_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_id INTEGER,
            action TEXT, -- 'created', 'updated', 'status_changed', 'cancelled', 'approved', 'rejected'
            old_data TEXT, -- JSON - avvalgi ma'lumotlar
            new_data TEXT, -- JSON - yangi ma'lumotlar
            field_name TEXT, -- qaysi maydon o'zgartirildi
            old_value TEXT,
            new_value TEXT,
            changed_by INTEGER, -- kim o'zgartirdi
            created_at TEXT,
            FOREIGN KEY (ad_id) REFERENCES ads (id),
            FOREIGN KEY (changed_by) REFERENCES users (user_id)
        )
    ''')

    # Categories (for employer jobs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            created_at TEXT
        )
    ''')

    # Student messages (for student suggestions/complaints)
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

    # Default categories qo'shish
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

def add_user(user_id: int, username: str, role: str = None, language: str = None):
    """Foydalanuvchi qo'shish yoki yangilash"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    exists = cursor.fetchone()
    
    if exists:
        # Faqat role va language ni yangilash
        cursor.execute('''
            UPDATE users SET username = ?, role = COALESCE(?, role), 
            language = COALESCE(?, language) WHERE user_id = ?
        ''', (username, role, language, user_id))
    else:
        cursor.execute('''
            INSERT INTO users (user_id, username, role, language, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, role, language or 'uz', datetime.utcnow().isoformat()))
    
    conn.commit()
    conn.close()

def add_ad(user_id: int, ad_type: str, data: dict, file_id: str = None, file_path: str = None, status: str = "draft"):
    """E'lon qo'shish"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    cursor.execute('''
        INSERT INTO ads (user_id, ad_type, status, data, file_id, file_path, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, ad_type, status, json.dumps(data, ensure_ascii=False), file_id, file_path, now, now))
    
    ad_id = cursor.lastrowid
    
    # History ga yozish
    cursor.execute('''
        INSERT INTO ad_history (ad_id, action, new_data, changed_by, created_at)
        VALUES (?, 'created', ?, ?, ?)
    ''', (ad_id, json.dumps(data, ensure_ascii=False), user_id, now))
    
    conn.commit()
    conn.close()
    return ad_id

def update_ad_status(ad_id: int, status: str, approved_by: int = None):
    """E'lon statusini yangilash"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Avvalgi statusni olish
    cursor.execute('SELECT status FROM ads WHERE id = ?', (ad_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False
    
    old_status = result[0]
    now = datetime.utcnow().isoformat()
    
    # Statusni yangilash
    if status == 'approved' and approved_by:
        cursor.execute('''
            UPDATE ads SET status = ?, updated_at = ?, approved_at = ?, approved_by = ?
            WHERE id = ?
        ''', (status, now, now, approved_by, ad_id))
    else:
        cursor.execute('''
            UPDATE ads SET status = ?, updated_at = ? WHERE id = ?
        ''', (status, now, ad_id))
    
    # History ga yozish
    cursor.execute('''
        INSERT INTO ad_history (ad_id, action, old_value, new_value, changed_by, created_at)
        VALUES (?, 'status_changed', ?, ?, ?, ?)
    ''', (ad_id, old_status, status, approved_by or 0, now))
    
    conn.commit()
    conn.close()
    return True

def update_ad_data(ad_id: int, new_data: dict, new_file_id: str = None, new_file_path: str = None):
    """E'lon ma'lumotlarini yangilash"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Avvalgi ma'lumotlarni olish
    cursor.execute('SELECT data, file_id FROM ads WHERE id = ?', (ad_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False

    old_data_json, old_file_id = result
    now = datetime.utcnow().isoformat()

    if new_file_id and new_file_path:
        cursor.execute('''
            UPDATE ads SET data = ?, file_id = ?, file_path = ?, updated_at = ?
            WHERE id = ?
        ''', (json.dumps(new_data, ensure_ascii=False), new_file_id, new_file_path, now, ad_id))
    elif new_file_id:
        cursor.execute('''
            UPDATE ads SET data = ?, file_id = ?, updated_at = ?
            WHERE id = ?
        ''', (json.dumps(new_data, ensure_ascii=False), new_file_id, now, ad_id))
    else:
        cursor.execute('''
            UPDATE ads SET data = ?, updated_at = ?
            WHERE id = ?
        ''', (json.dumps(new_data, ensure_ascii=False), now, ad_id))

    # History ga yozish
    cursor.execute('''
        INSERT INTO ad_history (ad_id, action, old_data, new_data, changed_by, created_at)
        VALUES (?, 'updated', ?, ?, ?, ?)
    ''', (ad_id, old_data_json, json.dumps(new_data, ensure_ascii=False), 0, now))

    conn.commit()
    conn.close()
    return True

def update_ad_field(ad_id: int, field_name: str, old_value: str, new_value: str, changed_by: int):
    """E'lonning bitta maydonini yangilash"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Hozirgi ma'lumotlarni olish
    cursor.execute('SELECT data FROM ads WHERE id = ?', (ad_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False
    
    ad_data = json.loads(result[0])
    ad_data[field_name] = new_value
    
    now = datetime.utcnow().isoformat()
    
    # Ma'lumotlarni yangilash
    cursor.execute('''
        UPDATE ads SET data = ?, updated_at = ? WHERE id = ?
    ''', (json.dumps(ad_data, ensure_ascii=False), now, ad_id))
    
    # History ga yozish
    cursor.execute('''
        INSERT INTO ad_history (ad_id, action, field_name, old_value, new_value, changed_by, created_at)
        VALUES (?, 'field_updated', ?, ?, ?, ?, ?)
    ''', (ad_id, field_name, old_value, new_value, changed_by, now))
    
    conn.commit()
    conn.close()
    return True

def get_user(user_id: int):
    """Foydalanuvchi ma'lumotlarini olish"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_ad(ad_id: int):
    """E'lon ma'lumotlarini olish"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ads WHERE id = ?', (ad_id,))
    ad = cursor.fetchone()
    conn.close()
    return ad

def get_user_ads(user_id: int):
    """Foydalanuvchi e'lonlarini olish - DELETED statusni yashirish"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM ads WHERE user_id = ? AND status != 'deleted'
        ORDER BY created_at DESC
    ''', (user_id,))
    ads = cursor.fetchall()
    conn.close()
    return ads


def get_pending_ads(ad_type: str = None):
    """Kutilayotgan e'lonlarni olish"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    if ad_type:
        cursor.execute('''
            SELECT * FROM ads WHERE status = 'pending' AND ad_type = ?
            ORDER BY created_at ASC
        ''', (ad_type,))
    else:
        cursor.execute('''
            SELECT * FROM ads WHERE status = 'pending'
            ORDER BY created_at ASC
        ''')
    
    ads = cursor.fetchall()
    conn.close()
    return ads

def get_categories():
    """Kategoriyalarni olish"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM categories ORDER BY name')
    categories = cursor.fetchall()
    conn.close()
    return categories

def add_category(name: str):
    """Yangi kategoriya qo'shish"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO categories (name, created_at) VALUES (?, ?)
    ''', (name, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_ad_history(ad_id: int):
    """E'lon tarixini olish"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM ad_history WHERE ad_id = ? 
        ORDER BY created_at DESC
    ''', (ad_id,))
    history = cursor.fetchall()
    conn.close()
    return history

def get_user_stats():
    """Foydalanuvchi statistikasi"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'graduate'")
    graduates = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'employer'")
    employers = cursor.fetchone()[0]
    
    conn.close()
    return {
        'total': total,
        'graduates': graduates,
        'employers': employers
    }

def get_approved_ads_by_category(category_name: str, limit: int = 20):
    """Kategoriya bo'yicha tasdiqlangan e'lonlarni olish (graduate va employer).
    Graduate uchun 'profession', employer uchun 'category' maydonlari bo'yicha filtrlanadi.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM ads WHERE status = 'approved' ORDER BY approved_at DESC NULLS LAST, created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        # row: (id, user_id, ad_type, status, data, file_id, file_path, created_at, updated_at, approved_at, approved_by)
        try:
            data = json.loads(row[4])
        except Exception:
            continue
        if row[2] == 'employer' and data.get('category') == category_name:
            results.append(row)
        elif row[2] == 'graduate' and data.get('profession') == category_name:
            results.append(row)
        if len(results) >= limit:
            break
    return results

def get_ad_stats():
    """E'lon statistikasi"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM ads')
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ads WHERE status = 'approved'")
    approved = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ads WHERE status = 'pending'")
    pending = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ads WHERE status = 'rejected'")
    rejected = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ads WHERE status = 'cancelled'")
    cancelled = cursor.fetchone()[0]
    
    conn.close()
    return {
        'total': total,
        'approved': approved,
        'pending': pending,
        'rejected': rejected,
        'cancelled': cancelled
    }