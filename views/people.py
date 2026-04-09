import streamlit as st
import pandas as pd
from database import run_query, run_update, get_all_students, get_all_teachers, get_all_rooms, set_active_status, delete_entity, reset_teacher_password

@st.dialog("Edit Student")
def edit_student_dialog(student_id):
    df = get_all_students()
    student_data = df[df['id'] == student_id].iloc[0]
    with st.form("edit_student_form_dialog"):
        new_name = st.text_input("Name", value=student_data['name'])
        new_grade = st.text_input("Grade", value=student_data['grade'])
        new_parent = st.text_input("Parent Name", value=student_data['parent_name'])
        new_mobile = st.text_input("Mobile", value=student_data['mobile'])
        new_email = st.text_input("Email", value=student_data['email'])
        
        if st.form_submit_button("Update Student"):
            if new_name:
                run_update("""
                    UPDATE Students 
                    SET name = :name, grade = :grade, parent_name = :parent, mobile = :mobile, email = :email 
                    WHERE id = :id
                """, {"name": new_name, "grade": new_grade, "parent": new_parent, "mobile": new_mobile, "email": new_email, "id": student_id})
                st.success("Student updated!")
                st.rerun()
            else:
                st.error("Name is required.")

@st.dialog("Delete Student")
def delete_student_dialog(student_id, student_name):
    st.warning(f"Are you sure you want to permanently delete **{student_name}**? This will remove all their enrollment and attendance history.")
    if st.button("Yes, Delete"):
        delete_entity('Students', student_id)
        st.success("Student deleted.")
        st.rerun()

@st.dialog("Edit Teacher")
def edit_teacher_dialog(teacher_id):
    df = get_all_teachers()
    teacher_data = df[df['id'] == teacher_id].iloc[0]
    with st.form("edit_teacher_form_dialog"):
        new_name = st.text_input("Teacher Name", value=teacher_data['name'])
        new_subject = st.text_input("Subject", value=teacher_data['subject'])
        new_rate = st.number_input("Hourly Rate", min_value=0.0, format="%.2f", value=float(teacher_data['hourly_rate']))
        new_phone = st.text_input("Phone", value=teacher_data['phone'])
        
        if st.form_submit_button("Update Teacher"):
            if new_name:
                run_update("""
                    UPDATE Teachers 
                    SET name = :name, subject = :subject, hourly_rate = :rate, phone = :phone 
                    WHERE id = :id
                """, {"name": new_name, "subject": new_subject, "rate": new_rate, "phone": new_phone, "id": teacher_id})
                run_update("UPDATE Users SET full_name = :name WHERE teacher_id = :id", {"name": new_name, "id": teacher_id})
                st.success("Teacher updated!")
                st.rerun()
            else:
                st.error("Name is required.")

@st.dialog("Delete Teacher")
def delete_teacher_dialog(teacher_id, teacher_name):
    st.warning(f"Are you sure you want to permanently delete **{teacher_name}**? Their classes will become 'No Teacher'.")
    if st.button("Yes, Delete"):
        delete_entity('Teachers', teacher_id)
        st.success("Teacher deleted.")
        st.rerun()

@st.dialog("Edit Room")
def edit_room_dialog(room_id):
    df = get_all_rooms()
    room_data = df[df['id'] == room_id].iloc[0]
    with st.form("edit_room_form_dialog"):
        new_name = st.text_input("Room Name/Number", value=room_data['name'])
        new_capacity = st.number_input("Capacity", min_value=1, value=int(room_data['capacity']))
        
        if st.form_submit_button("Update Room"):
            if new_name:
                run_update("""
                    UPDATE Rooms 
                    SET name = :name, capacity = :cap 
                    WHERE id = :id
                """, {"name": new_name, "cap": new_capacity, "id": room_id})
                st.success("Room updated!")
                st.rerun()
            else:
                st.error("Room name is required.")

@st.dialog("Delete Room")
def delete_room_dialog(room_id, room_name):
    st.warning(f"Are you sure you want to permanently delete **{room_name}**? Their classes will become 'No Room'.")
    if st.button("Yes, Delete"):
        delete_entity('Rooms', room_id)
        st.success("Room deleted.")
        st.rerun()

@st.dialog("Reset Teacher Password")
def reset_pwd_dialog(teacher_id, teacher_name):
    st.write(f"Reset password for **{teacher_name}**")
    new_pwd = st.text_input("New Password", type="password")
    if st.button("Update Password"):
        if new_pwd:
            import bcrypt
            hashed_pw = bcrypt.hashpw(new_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            reset_teacher_password(teacher_id, hashed_pw)
            st.success("Password reset!")
            st.rerun()
        else:
            st.error("Enter a password.")

def show_people():
    st.title("People & Resources")
    
    tab1, tab2, tab3 = st.tabs(["Students", "Teachers", "Rooms"])
    
    with tab1:
        st.header("Students")
        show_inactive = st.checkbox("Show Inactive Students", key="show_inactive_students")
        df_students = get_all_students(only_active=not show_inactive)
        
        if not df_students.empty:
            # Table Header
            hcol1, hcol2, hcol3, hcol4, hcol5 = st.columns([2, 1, 2, 1, 3])
            hcol1.write("**Name**")
            hcol2.write("**Grade**")
            hcol3.write("**Parent**")
            hcol4.write("**Active**")
            hcol5.write("**Actions**")
            st.divider()
            
            # Rows
            for _, student in df_students.iterrows():
                rcol1, rcol2, rcol3, rcol4, rcol5 = st.columns([2, 1, 2, 1, 3])
                rcol1.write(student['name'])
                rcol2.write(student['grade'])
                rcol3.write(student['parent_name'])
                
                # Active Toggle
                status_text = "✅" if student['is_active'] else "❌"
                if rcol4.button(status_text, key=f"tog_std_{student['id']}"):
                    set_active_status('Students', student['id'], not student['is_active'])
                    st.rerun()
                
                # Action Buttons
                with rcol5:
                    acol1, acol2 = st.columns(2)
                    if acol1.button("Modify", key=f"edit_std_{student['id']}"):
                        edit_student_dialog(student['id'])
                    if acol2.button("Delete", key=f"del_std_{student['id']}"):
                        delete_student_dialog(student['id'], student['name'])
        else:
            st.info("No students found.")
        
        with st.expander("➕ Add New Student"):
            with st.form("add_student_form"):
                name = st.text_input("Name")
                grade = st.text_input("Grade")
                parent_name = st.text_input("Parent Name")
                mobile = st.text_input("Mobile")
                email = st.text_input("Email")
                if st.form_submit_button("Add Student"):
                    if name:
                        run_update("INSERT INTO Students (name, grade, parent_name, mobile, email, is_active) VALUES (:name, :grade, :parent, :mobile, :email, TRUE)", 
                                   {"name": name, "grade": grade, "parent": parent_name, "mobile": mobile, "email": email})
                        st.success(f"Added student: {name}")
                        st.rerun()
                    else:
                        st.error("Name is required.")
                        
    with tab2:
        st.header("Teachers")
        show_inactive_t = st.checkbox("Show Inactive Teachers", key="show_inactive_teachers")
        df_teachers = get_all_teachers(only_active=not show_inactive_t)
        
        if not df_teachers.empty:
            # Table Header
            hcol1, hcol2, hcol3, hcol4, hcol5 = st.columns([2, 2, 1, 1, 4])
            hcol1.write("**Name**")
            hcol2.write("**Subject**")
            hcol3.write("**Rate**")
            hcol4.write("**Active**")
            hcol5.write("**Actions**")
            st.divider()
            
            for _, teacher in df_teachers.iterrows():
                rcol1, rcol2, rcol3, rcol4, rcol5 = st.columns([2, 2, 1, 1, 4])
                rcol1.write(teacher['name'])
                rcol2.write(teacher['subject'])
                rcol3.write(f"${teacher['hourly_rate']}")
                
                status_text = "✅" if teacher['is_active'] else "❌"
                if rcol4.button(status_text, key=f"tog_tea_{teacher['id']}"):
                    set_active_status('Teachers', teacher['id'], not teacher['is_active'])
                    st.rerun()
                
                with rcol5:
                    acol1, acol2, acol3 = st.columns(3)
                    if acol1.button("Modify", key=f"edit_tea_{teacher['id']}"):
                        edit_teacher_dialog(teacher['id'])
                    if acol2.button("Delete", key=f"del_tea_{teacher['id']}"):
                        delete_teacher_dialog(teacher['id'], teacher['name'])
                    if acol3.button("Reset Pwd", key=f"pwd_tea_{teacher['id']}"):
                        reset_pwd_dialog(teacher['id'], teacher['name'])
        else:
            st.info("No teachers found.")
        
        with st.expander("➕ Add New Teacher"):
            with st.form("add_teacher_form"):
                name = st.text_input("Teacher Name")
                subject = st.text_input("Subject")
                hourly_rate = st.number_input("Hourly Rate", min_value=0.0, format="%.2f")
                phone = st.text_input("Phone")
                if st.form_submit_button("Add Teacher"):
                    if name:
                        teacher_id = run_update("INSERT INTO Teachers (name, subject, hourly_rate, phone, is_active) VALUES (:name, :subject, :rate, :phone, TRUE)", 
                                   {"name": name, "subject": subject, "rate": hourly_rate, "phone": phone})
                        import bcrypt
                        default_pw = "password123"
                        hashed_pw = bcrypt.hashpw(default_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        run_update("INSERT INTO Users (username, password_hash, role, teacher_id, full_name, is_active) VALUES (:un, :pw, 'Teacher', :tid, :name, TRUE)", 
                                   {"un": name.lower().replace(" ", "_"), "pw": hashed_pw, "tid": teacher_id, "name": name})
                        st.success(f"Added teacher: {name}")
                        st.rerun()
                    else:
                        st.error("Name is required.")

    with tab3:
        st.header("Rooms")
        show_inactive_r = st.checkbox("Show Inactive Rooms", key="show_inactive_rooms")
        df_rooms = get_all_rooms(only_active=not show_inactive_r)
        
        if not df_rooms.empty:
            # Table Header
            hcol1, hcol2, hcol3, hcol4 = st.columns([3, 2, 1, 3])
            hcol1.write("**Room Name**")
            hcol2.write("**Capacity**")
            hcol3.write("**Active**")
            hcol4.write("**Actions**")
            st.divider()
            
            for _, room in df_rooms.iterrows():
                rcol1, rcol2, rcol3, rcol4 = st.columns([3, 2, 1, 3])
                rcol1.write(room['name'])
                rcol2.write(str(room['capacity']))
                
                status_text = "✅" if room['is_active'] else "❌"
                if rcol3.button(status_text, key=f"tog_rom_{room['id']}"):
                    set_active_status('Rooms', room['id'], not room['is_active'])
                    st.rerun()
                
                with rcol4:
                    acol1, acol2 = st.columns(2)
                    if acol1.button("Modify", key=f"edit_rom_{room['id']}"):
                        edit_room_dialog(room['id'])
                    if acol2.button("Delete", key=f"del_rom_{room['id']}"):
                        delete_room_dialog(room['id'], room['name'])
        else:
            st.info("No rooms found.")
        
        with st.expander("➕ Add New Room"):
            with st.form("add_room_form"):
                name = st.text_input("Room Name/Number")
                capacity = st.number_input("Capacity", min_value=1, value=10)
                if st.form_submit_button("Add Room"):
                    if name:
                        run_update("INSERT INTO Rooms (name, capacity, is_active) VALUES (:name, :cap, TRUE)", 
                                   {"name": name, "cap": capacity})
                        st.success(f"Added room: {name}")
                        st.rerun()
                    else:
                        st.error("Room name is required.")
