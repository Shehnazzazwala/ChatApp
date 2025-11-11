# crypto.py

from cryptography.fernet import Fernet

def generate_key():
    """Generates a new encryption key."""
    return Fernet.generate_key()

# --- For Text ---
def encrypt_message(message, key):
    """Encrypts a text message using the provided key."""
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message

def decrypt_message(encrypted_message, key):
    """Decrypts a text message using the provided key."""
    f = Fernet(key)
    try:
        decrypted_message = f.decrypt(encrypted_message).decode()
        return decrypted_message
    except Exception as e:
        print(f"Decryption failed: {e}")
        return "⚠️ This message could not be decrypted."

# --- THIS IS NEW (For Files) ---
def encrypt_bytes(data_bytes, key):
    """Encrypts raw bytes using the provided key."""
    f = Fernet(key)
    encrypted_bytes = f.encrypt(data_bytes)
    return encrypted_bytes

def decrypt_bytes(encrypted_bytes, key):
    """Decrypts raw bytes using the provided key."""
    f = Fernet(key)
    try:
        decrypted_bytes = f.decrypt(encrypted_bytes)
        return decrypted_bytes
    except Exception as e:
        print(f"File decryption failed: {e}")
        return None
# --- END OF NEW ---