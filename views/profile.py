import streamlit as st
import bcrypt
from database import update_user_password

def show_profile():
    st.title("My Profile & Security")
    
    user_id = st.session_state.get('user_id')
    username = st.session_state.get('username')
    full_name = st.session_state.get('full_name', username)
    role = st.session_state.get('role')
    
    st.write(f"**Username:** {username}")
    st.write(f"**Full Name:** {full_name}")
    st.write(f"**Role:** {role}")
    
    st.divider()
    st.subheader("Change Password")
    
    with st.form("change_password_form"):
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submit_button = st.form_submit_button("Update Password")
        
        if submit_button:
            if not new_password:
                st.error("Password cannot be empty.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                update_user_password(user_id, hashed_pw)
                st.success("Password updated successfully!")
