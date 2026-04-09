import streamlit as st
import pandas as pd
from database import run_query, run_update, get_all_students, get_all_teachers, get_all_rooms, set_active_status, delete_entity, reset_teacher_password

def show_people():
    st.title("People & Resources")
    
    tab1, tab2, tab3 = st.tabs(["Students", "Teachers", "Rooms"])
    
    with tab1:
        st.header("Students")
        
        # Filter for active/inactive
        show_inactive = st.checkbox("Show Inactive Students", key="show_inactive_students")
        df_students = get_all_students(only_active=not show_inactive)
        
        if not df_students.empty:
            # Display student table with basic info
            st.dataframe(df_students[['id', 'name', 'grade', 'parent_name', 'mobile', 'is_active']], use_container_width=True)
            
            # Action section for individual student
            st.subheader("Student Actions")
            student_to_manage = st.selectbox("Select Student to Manage", 
                                            options=df_students['id'].tolist(),
                                            format_func=lambda x: df_students[df_students['id'] == x]['name'].values[0])
            
            col1, col2 = st.columns(2)
            with col1:
                current_active = df_students[df_students['id'] == student_to_manage]['is_active'].values[0]
                if st.button("Activate" if not current_active else "Deactivate", key="toggle_student"):
                    set_active_status('Students', student_to_manage, not current_active)
                    st.success(f"Student status updated.")
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete Student", key="delete_student"):
                    delete_entity('Students', student_to_manage)
                    st.success(f"Student deleted.")
                    st.rerun()
        else:
            st.info("No students found.")
        
        with st.expander("Add New Student"):
            with st.form("add_student_form"):
                name = st.text_input("Name")
                grade = st.text_input("Grade")
                parent_name = st.text_input("Parent Name")
                mobile = st.text_input("Mobile")
                email = st.text_input("Email")
                submitted = st.form_submit_button("Add Student")
                
                if submitted:
                    if name:
                        run_update("INSERT INTO Students (name, grade, parent_name, mobile, email, is_active) VALUES (?, ?, ?, ?, ?, 1)", 
                                   (name, grade, parent_name, mobile, email))
                        st.success(f"Added student: {name}")
                        st.rerun()
                    else:
                        st.error("Name is required.")
                        
    with tab2:
        st.header("Teachers")
        
        # Filter for active/inactive
        show_inactive_t = st.checkbox("Show Inactive Teachers", key="show_inactive_teachers")
        df_teachers = get_all_teachers(only_active=not show_inactive_t)
        
        if not df_teachers.empty:
            st.dataframe(df_teachers[['id', 'name', 'subject', 'hourly_rate', 'is_active']], use_container_width=True)
            
            st.subheader("Teacher Actions")
            teacher_to_manage = st.selectbox("Select Teacher to Manage", 
                                            options=df_teachers['id'].tolist(),
                                            format_func=lambda x: df_teachers[df_teachers['id'] == x]['name'].values[0])
            
            col1, col2 = st.columns(2)
            with col1:
                current_active_t = df_teachers[df_teachers['id'] == teacher_to_manage]['is_active'].values[0]
                if st.button("Activate" if not current_active_t else "Deactivate", key="toggle_teacher"):
                    set_active_status('Teachers', teacher_to_manage, not current_active_t)
                    st.success(f"Teacher status updated.")
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete Teacher", key="delete_teacher"):
                    delete_entity('Teachers', teacher_to_manage)
                    st.success(f"Teacher deleted.")
                    st.rerun()
            
            # Admin Reset Teacher Password
            st.divider()
            st.write("**Admin: Reset Teacher Password**")
            new_pwd = st.text_input("New Password for Teacher", type="password", key="reset_pwd_input")
            if st.button("Reset Password", key="reset_pwd_btn"):
                if new_pwd:
                    import bcrypt
                    hashed_pw = bcrypt.hashpw(new_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    reset_teacher_password(teacher_to_manage, hashed_pw)
                    st.success("Teacher password reset successfully!")
                else:
                    st.error("Please enter a new password.")
        else:
            st.info("No teachers found.")
        
        with st.expander("Add New Teacher"):
            with st.form("add_teacher_form"):
                name = st.text_input("Teacher Name")
                subject = st.text_input("Subject")
                hourly_rate = st.number_input("Hourly Rate", min_value=0.0, format="%.2f")
                phone = st.text_input("Phone")
                submitted = st.form_submit_button("Add Teacher")
                
                if submitted:
                    if name:
                        teacher_id = run_update("INSERT INTO Teachers (name, subject, hourly_rate, phone, is_active) VALUES (?, ?, ?, ?, 1)", 
                                   (name, subject, hourly_rate, phone))
                        
                        # Create a corresponding User account (default password is name + 123)
                        import bcrypt
                        default_pw = "password123"
                        hashed_pw = bcrypt.hashpw(default_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        run_update("INSERT INTO Users (username, password_hash, role, teacher_id, full_name, is_active) VALUES (?, ?, ?, ?, ?, 1)", 
                                   (name.lower().replace(" ", "_"), hashed_pw, 'Teacher', teacher_id, name))
                        
                        st.success(f"Added teacher: {name} (User account created)")
                        st.rerun()
                    else:
                        st.error("Name is required.")

    with tab3:
        st.header("Rooms")
        
        # Filter for active/inactive
        show_inactive_r = st.checkbox("Show Inactive Rooms", key="show_inactive_rooms")
        df_rooms = get_all_rooms(only_active=not show_inactive_r)
        
        if not df_rooms.empty:
            st.dataframe(df_rooms[['id', 'name', 'capacity', 'is_active']], use_container_width=True)
            
            st.subheader("Room Actions")
            room_to_manage = st.selectbox("Select Room to Manage", 
                                            options=df_rooms['id'].tolist(),
                                            format_func=lambda x: df_rooms[df_rooms['id'] == x]['name'].values[0])
            
            col1, col2 = st.columns(2)
            with col1:
                current_active_r = df_rooms[df_rooms['id'] == room_to_manage]['is_active'].values[0]
                if st.button("Activate" if not current_active_r else "Deactivate", key="toggle_room"):
                    set_active_status('Rooms', room_to_manage, not current_active_r)
                    st.success(f"Room status updated.")
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete Room", key="delete_room"):
                    delete_entity('Rooms', room_to_manage)
                    st.success(f"Room deleted.")
                    st.rerun()
        else:
            st.info("No rooms found.")
        
        with st.expander("Add New Room"):
            with st.form("add_room_form"):
                name = st.text_input("Room Name/Number")
                capacity = st.number_input("Capacity", min_value=1, value=10)
                submitted = st.form_submit_button("Add Room")
                
                if submitted:
                    if name:
                        run_update("INSERT INTO Rooms (name, capacity, is_active) VALUES (?, ?, 1)", (name, capacity))
                        st.success(f"Added room: {name}")
                        st.rerun()
                    else:
                        st.error("Room name is required.")
