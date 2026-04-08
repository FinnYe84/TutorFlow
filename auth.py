import streamlit as st
import bcrypt
from database import get_user_by_username

def login():
    st.title("TutorFlow Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = get_user_by_username(username)
        if user:
            # Check if user is active
            if user.get('is_active') == 0:
                st.error("This account has been deactivated. Please contact the administrator.")
                return
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.session_state['role'] = user['role']
                st.session_state['user_id'] = user['id']
                st.session_state['teacher_id'] = user['teacher_id']
                st.success(f"Logged in as {user['full_name']}")
                st.rerun()
            else:
                st.error("Invalid username or password")
        else:
            st.error("Invalid username or password")

def logout():
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.session_state['role'] = None
    st.session_state.clear()
    st.rerun()

def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    if not st.session_state['authenticated']:
        login()
        return False
    return True
