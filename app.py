import streamlit as st
from auth import check_auth, logout

# Page Config
st.set_page_config(page_title="TutorFlow Sydney", layout="wide")

# Check authentication
if check_auth():
    # Sidebar Navigation
    st.sidebar.title(f"Welcome, {st.session_state.get('username')}")
    st.sidebar.write(f"Role: {st.session_state.get('role')}")
    
    if st.sidebar.button("Logout"):
        logout()
    
    # Navigation menu
    pages = {
        "Dashboard": "dashboard",
        "People": "people",
        "Class Setup": "class_setup",
        "Attendance": "attendance",
        "Settings": "settings",
        "My Profile": "profile"
    }
    
    # Remove certain pages if role is Teacher
    if st.session_state.get('role') == 'Teacher':
        pages.pop("People")
        pages.pop("Class Setup")
        pages.pop("Settings")
        
    choice = st.sidebar.radio("Navigation", list(pages.keys()))
    
    # Route to the selected page
    if choice == "Dashboard":
        from views.dashboard import show_dashboard
        show_dashboard()
    elif choice == "People":
        from views.people import show_people
        show_people()
    elif choice == "Class Setup":
        from views.class_setup import show_class_setup
        show_class_setup()
    elif choice == "Attendance":
        from views.attendance import show_attendance
        show_attendance()
    elif choice == "Settings":
        from views.settings import show_settings
        show_settings()
    elif choice == "My Profile":
        from views.profile import show_profile
        show_profile()
