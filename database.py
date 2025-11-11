# database.py

import sqlite3

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect('chat_app.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Creates the necessary tables for users, messages, and conversation keys."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_username TEXT NOT NULL,
                receiver_username TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                message_type TEXT NOT NULL DEFAULT 'text', 
                encrypted_message TEXT,
                encrypted_file_path TEXT,
                original_filename TEXT,

                FOREIGN KEY (sender_username) REFERENCES users (username),
                FOREIGN KEY (receiver_username) REFERENCES users (username)
            );
        """)
        
        # --- THIS IS THE CHANGE ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_username TEXT NOT NULL,
                user2_username TEXT NOT NULL,
                shared_key BLOB NOT NULL,
                user1_pin TEXT, -- Can be NULL
                user2_pin TEXT, -- Can be NULL
                UNIQUE (user1_username, user2_username)
            );
        """)
        # --- END OF CHANGE ---
        
        conn.commit()
        print("Database and all tables (users, messages, conversations) created successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    create_tables()