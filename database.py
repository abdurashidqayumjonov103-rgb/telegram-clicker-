import sqlite3
import hmac
import hashlib
import json
from urllib.parse import parse_qsl

DB_NAME = "clicker.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0,
            click_level INTEGER DEFAULT 1,
            referrals_count INTEGER DEFAULT 0,
            referred_by INTEGER,
            last_bonus TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def verify_telegram_data(init_data: str, bot_token: str) -> dict | None:
    try:
        parsed_data = dict(parse_qsl(init_data))
        if 'hash' not in parsed_data:
            return None
        
        hash_val = parsed_data.pop('hash')
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if calculated_hash == hash_val:
            return json.loads(parsed_data.get('user', '{}'))
        return None
    except Exception:
        return None

def get_or_create_user(user_id: int, username: str, referrer_id: int = None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, username, referred_by) VALUES (?, ?, ?)",
            (user_id, username, referrer_id)
        )
        if referrer_id:
            cursor.execute(
                "UPDATE users SET referrals_count = referrals_count + 1, balance = balance + 500 WHERE user_id = ?",
                (referrer_id,)
            )
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
    conn.close()
    return dict(user)
