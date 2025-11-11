# chat.py

import sqlite3
from database import get_db_connection
from crypto import (
    generate_key, 
    encrypt_message, decrypt_message,
    encrypt_bytes, decrypt_bytes
)
import os
import uuid
from auth import hash_password # Import the hashing function


def get_or_create_shared_key(user1, user2):
    """Gets the shared key for two users, creating one if it doesn't exist."""
    users = sorted([user1, user2])
    u1, u2 = users[0], users[1]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT shared_key FROM conversations WHERE user1_username = ? AND user2_username = ?",
        (u1, u2)
    )
    result = cursor.fetchone()
    if result:
        conn.close()
        return result['shared_key']
    else:
        new_key = generate_key()
        cursor.execute(
            "INSERT INTO conversations (user1_username, user2_username, shared_key) VALUES (?, ?, ?)",
            (u1, u2, new_key)
        )
        conn.commit()
        conn.close()
        return new_key

# --- ALL OF THE FOLLOWING FUNCTIONS ARE NEW ---

def set_chat_pin(current_user, chat_partner, pin):
    """Sets or updates the PIN for the current user for a specific chat."""
    users = sorted([current_user, chat_partner])
    u1, u2 = users[0], users[1]
    hashed_pin = hash_password(pin)
    
    pin_column = "user1_pin" if current_user == u1 else "user2_pin"

    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"UPDATE conversations SET {pin_column} = ? WHERE user1_username = ? AND user2_username = ?"
    cursor.execute(query, (hashed_pin, u1, u2))
    conn.commit()
    conn.close()

def is_pin_set(current_user, chat_partner):
    """Checks if the current user has set a PIN for this chat."""
    users = sorted([current_user, chat_partner])
    u1, u2 = users[0], users[1]
    
    pin_column = "user1_pin" if current_user == u1 else "user2_pin"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT {pin_column} FROM conversations WHERE user1_username = ? AND user2_username = ?"
    cursor.execute(query, (u1, u2))
    result = cursor.fetchone()
    conn.close()

    # If a conversation row exists and the PIN column is not NULL, a PIN is set.
    return result is not None and result[pin_column] is not None

def verify_chat_pin(current_user, chat_partner, submitted_pin):
    """Verifies the submitted PIN against the stored hashed PIN."""
    users = sorted([current_user, chat_partner])
    u1, u2 = users[0], users[1]
    hashed_submitted_pin = hash_password(submitted_pin)
    
    pin_column = "user1_pin" if current_user == u1 else "user2_pin"

    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT {pin_column} FROM conversations WHERE user1_username = ? AND user2_username = ?"
    cursor.execute(query, (u1, u2))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[pin_column]:
        return result[pin_column] == hashed_submitted_pin
    return False

# --- END OF NEW FUNCTIONS ---


def add_private_message(sender, receiver, message_text=None, uploaded_file=None):
    # (This function remains unchanged)
    key = get_or_create_shared_key(sender, receiver)
    conn = get_db_connection()
    cursor = conn.cursor()

    if message_text:
        encrypted_text = encrypt_message(message_text, key)
        cursor.execute(
            """
            INSERT INTO messages (sender_username, receiver_username, message_type, encrypted_message) 
            VALUES (?, ?, ?, ?)
            """,
            (sender, receiver, 'text', encrypted_text)
        )
    
    elif uploaded_file:
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        encrypted_filename = f"{uuid.uuid4().hex}.enc"
        encrypted_file_path = os.path.join(uploads_dir, encrypted_filename)
        file_bytes = uploaded_file.read()
        encrypted_bytes = encrypt_bytes(file_bytes, key)
        with open(encrypted_file_path, "wb") as f:
            f.write(encrypted_bytes)
        file_type = uploaded_file.type.split('/')[0]
        message_type = 'image' if file_type == 'image' else 'file'
        cursor.execute(
            """
            INSERT INTO messages (sender_username, receiver_username, message_type, 
                                  encrypted_file_path, original_filename) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (sender, receiver, message_type, encrypted_file_path, uploaded_file.name)
        )

    conn.commit()
    conn.close()


def get_private_messages(user1, user2):
    # (This function remains unchanged)
    key = get_or_create_shared_key(user1, user2)
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT * FROM messages
        WHERE (sender_username = ? AND receiver_username = ?)
           OR (sender_username = ? AND receiver_username = ?)
        ORDER BY timestamp ASC
    """
    cursor.execute(query, (user1, user2, user2, user1))
    messages = cursor.fetchall()
    conn.close()
    processed_msgs = []
    for msg in messages:
        msg_data = {
            'sender_username': msg['sender_username'],
            'timestamp': msg['timestamp'],
            'message_type': msg['message_type']
        }
        if msg['message_type'] == 'text':
            msg_data['message'] = decrypt_message(msg['encrypted_message'], key)
        else:
            msg_data['file_path'] = msg['encrypted_file_path']
            msg_data['filename'] = msg['original_filename']
        processed_msgs.append(msg_data)
    return processed_msgs