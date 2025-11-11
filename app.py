# app.py

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from auth import add_user, check_user, get_all_users
# We must import all chat functions needed
from chat import (
    get_private_messages, add_private_message, get_or_create_shared_key,
    set_chat_pin, is_pin_set, verify_chat_pin  # --- IMPORT NEW FUNCTIONS ---
)
from styles import load_css
from themes import THEMES
import io
from crypto import decrypt_bytes
from database import create_tables # <--- 1. IMPORT THE FUNCTION

create_tables() # <--- 2. CALL THE FUNCTION TO ENSURE TABLES ARE CREATED


# --- Page Configuration ---
st.set_page_config(page_title="ChatApp", page_icon="😊", layout="centered")
st_autorefresh(interval=2000, key="data_refresher")

def main():
    # --- Session State and CSS ---
    if 'logged_in' not in st.session_state:
        st.session_state.update({
            'logged_in': False, 'username': "",
            'chat_partner': None, 'theme': "Rose Petal",
            'unlocked_chats': {}  # --- NEW: Tracks which chats are unlocked ---
        })
    
    st.markdown(load_css(st.session_state['theme']), unsafe_allow_html=True)
    
    # --- Authentication Flow (remains unchanged) ---
    if not st.session_state['logged_in']:
        st.title("Hey there!")
        col1, col2, col3 = st.columns([1, 2, 1]) 
        with col2: 
            choice = st.selectbox("Login/Sign Up", ["Login", "Sign Up"], label_visibility="collapsed")
            if choice == "Login":
                st.subheader("Login")
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type='password', key="login_pass")
                if st.button("Login", use_container_width=True):
                    if check_user(username, password):
                        st.session_state.update({'logged_in': True, 'username': username})
                        st.rerun()
                    else: st.error("Incorrect username or password")
            else:
                st.subheader("Sign Up")
                new_user = st.text_input("New Username", key="signup_user")
                new_password = st.text_input("New Password", type='password', key="signup_pass")
                if st.button("Sign Up", use_container_width=True):
                    if add_user(new_user, new_password): 
                        st.success("Account created! Please login.")
                    else: st.error("Username taken.")
        return

    # --- Logged-In Interface ---
    
    # Sidebar Setup
    with st.sidebar:
        st.header(f"Welcome, {st.session_state['username']}!")
        users = get_all_users(st.session_state['username'])
        users.sort()
        if users:
            st.markdown("---")
            st.subheader("Contacts")
            default_index = 0
            if st.session_state['chat_partner'] in users:
                default_index = users.index(st.session_state['chat_partner'])
            elif st.session_state['chat_partner'] is None and users:
                st.session_state['chat_partner'] = users[0]
            
            selected_partner = st.radio(
                "Select a contact to chat with:", users, key='partner_select', index=default_index
            )
            
            # --- MODIFIED: Reset lock status when changing chats ---
            if selected_partner != st.session_state['chat_partner']:
                st.session_state['chat_partner'] = selected_partner
                st.session_state['unlocked_chats'] = {} # Lock all chats
                st.rerun()
            
            st.session_state['chat_partner'] = selected_partner
            
            # --- NEW: UI to set a chat PIN ---
            with st.expander("Chat Security"):
                st.caption(f"Set a PIN to lock your chat with {st.session_state['chat_partner']}.")
                new_pin = st.text_input(
                    "Enter 4-digit PIN", 
                    key=f"pin_for_{st.session_state['chat_partner']}", 
                    type="password", 
                    max_chars=4
                )
                if st.button("Set/Change PIN", key=f"set_pin_{st.session_state['chat_partner']}"):
                    if new_pin.isdigit() and len(new_pin) == 4:
                        set_chat_pin(st.session_state['username'], st.session_state['chat_partner'], new_pin)
                        st.success("PIN has been set for this chat!")
                    else:
                        st.warning("PIN must be 4 digits.")

        else:
            st.info("No other users registered yet.")

        # Theme Selector and Logout (remains unchanged)
        st.markdown("---")
        st.subheader("Theme")
        st.session_state['theme'] = st.selectbox(
            "Select a Theme:", list(THEMES.keys()), key="theme_selector", on_change=st.rerun,
            index=list(THEMES.keys()).index(st.session_state.get('theme', 'Rose Petal'))
        )
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- Chat Interface (Main Logic Change) ---
    if st.session_state['chat_partner']:
        partner = st.session_state['chat_partner']
        username = st.session_state['username']
        
        # --- NEW: Check if PIN is required and if chat is unlocked ---
        pin_required = is_pin_set(username, partner)
        is_unlocked = st.session_state.get('unlocked_chats', {}).get(partner, False)
        
        # --- A. SHOW THE LOCK SCREEN ---
        if pin_required and not is_unlocked:
            st.header(f"🔒 Chat with {partner} is locked")
            with st.form("pin_form"):
                pin_attempt = st.text_input("Enter PIN to unlock", type="password", max_chars=4)
                submitted = st.form_submit_button("Unlock")
                if submitted:
                    if verify_chat_pin(username, partner, pin_attempt):
                        st.session_state['unlocked_chats'][partner] = True
                        st.rerun()
                    else:
                        st.error("Incorrect PIN.")

        # --- B. SHOW THE CHAT INTERFACE (if not locked) ---
        else:
            # st.markdown('<div class="chat-page-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-header">{partner}</div>', unsafe_allow_html=True)
            chat_key = get_or_create_shared_key(username, partner)
            messages = get_private_messages(username, partner)
            st.markdown('<div class="chat-container">', unsafe_allow_html=True) 

            if not messages:
                st.markdown(
                    '<div class="empty-chat-message">Your chat history is empty. Send the first message!</div>',
                    unsafe_allow_html=True
                )
            else:
                # Message rendering loop (remains unchanged)
                for msg in messages:
                    is_user_message = (msg['sender_username'] == username)
                    row_class = "user-message-row" if is_user_message else "other-message-row"
                    message_class = "chat-message user-message" if is_user_message else "chat-message other-message"
                    if msg['message_type'] == 'text':
                        st.markdown(f"""
                            <div class="message-row {row_class}">
                                <div class="{message_class}">
                                    <span class="sender">{msg['sender_username']}</span>
                                    <div class="message-content">{msg['message']}</div> 
                                    <span class="timestamp">{msg['timestamp'].split('.')[0]}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="message-row {row_class}">
                                <div class="{message_class}">
                                    <span class="sender">{msg['sender_username']}</span>
                                    <div class="file-content">
                        """, unsafe_allow_html=True)
                        try:
                            with open(msg['file_path'], 'rb') as f: encrypted_bytes = f.read()
                            decrypted_bytes = decrypt_bytes(encrypted_bytes, chat_key)
                            if decrypted_bytes:
                                if msg['message_type'] == 'image':
                                    st.image(io.BytesIO(decrypted_bytes), caption=msg['filename'])
                                else:
                                    st.download_button(
                                        label=f"⬇️ Download {msg['filename']}", data=decrypted_bytes,
                                        file_name=msg['filename'], mime=msg['message_type']
                                    )
                            else: st.warning("⚠️ Could not decrypt file content.")
                        except FileNotFoundError: st.error("Error: Encrypted file not found.")
                        except Exception as e: st.error(f"An error occurred: {e}")
                        st.markdown(f"""
                                    </div><span class="timestamp">{msg['timestamp'].split('.')[0]}</span>
                                </div></div>
                        """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True) 
            
            # Message input form (remains unchanged)
            with st.form(key='message_form', clear_on_submit=True):
                col1, col2 = st.columns([5, 1])
                with col1:
                    message_text = st.text_input("Your message...", placeholder="Type...", label_visibility="collapsed")
                    uploaded_file = st.file_uploader("Attach a file", type=None, label_visibility="collapsed")
                with col2:
                    send_pressed = st.form_submit_button("Send", use_container_width=True) 
                if send_pressed:
                    if uploaded_file: add_private_message(sender=username, receiver=partner, uploaded_file=uploaded_file)
                    elif message_text: add_private_message(sender=username, receiver=partner, message_text=message_text)
                    else: st.toast("Please type a message or upload a file."); st.stop() 
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True) 

    else:
        st.info("Select a contact from the sidebar to start chatting.")

if __name__ == '__main__':
    main()