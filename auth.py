# auth.py

import hashlib
import sqlite3
from database import get_db_connection

def hash_password(password):
    """Hashes a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    """Adds a new user to the database."""
    # (This function remains unchanged)
    conn = get_db_connection()
    try:
        hashed_password = hash_password(password)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    """Verifies a user's credentials against the database."""
    # (This function remains unchanged)
    conn = get_db_connection()
    try:
        hashed_password = hash_password(password)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = cursor.fetchone()
        return user is not None
    finally:
        conn.close()

def get_all_users(current_username):
    """Retrieves all registered users except the current user."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username != ?", (current_username,))
        users = cursor.fetchall()
        return [user['username'] for user in users]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()