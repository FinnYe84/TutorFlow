import streamlit as st
import pandas as pd
from database import run_query, get_classes_for_teacher, get_all_classes, get_students_in_class, update_attendance, get_attendance, get_attendance_for_class

def show_attendance():
    st.title("Attendance Tracker")
    
    # Get relevant classes based on role
    if st.session_state.get('role') == 'Teacher':
        teacher_id = st.session_state.get('teacher_id')
        classes = get_classes_for_teacher(teacher_id)
    else:
        classes = get_all_classes()
        
    if classes.empty:
        st.info("No classes assigned to you.")
        return
        
    class_options = {f"{row['subject']} ({row['day_of_week']} {row['start_time']})": row['id'] for _, row in classes.iterrows()}
    selected_class_label = st.selectbox("Select Class", list(class_options.keys()))
    class_id = class_options[selected_class_label]
    
    # Attendance Grid (10 Weeks)
    students = get_students_in_class(class_id)
    if students.empty:
        st.info("No students enrolled in this class.")
        return
        
    st.write("Mark attendance for each week (1-10):")
    
    # Pre-fetch all attendance for this class to avoid N+1 queries
    attendance_df = get_attendance_for_class(class_id)
    # Create a lookup dictionary: (student_id, week_number) -> status
    attendance_lookup = {}
    if not attendance_df.empty:
        for _, row in attendance_df.iterrows():
            attendance_lookup[(row['student_id'], row['week_number'])] = row['status']
    
    # Track changes in session state
    if 'att_changes' not in st.session_state:
        st.session_state['att_changes'] = {}
    
    # Create attendance grid
    with st.form("attendance_form"):
        st.write("Mark attendance for each week (1-10) and click 'Save Changes' below.")
        
        for i, student in students.iterrows():
            st.subheader(student['name'])
            cols = st.columns(10)
            for week in range(1, 11):
                with cols[week-1]:
                    current_status = attendance_lookup.get((student['id'], week))
                    is_present = (current_status == 'Present')
                    
                    # We use checkboxes inside the form. They won't trigger reruns until submit.
                    st.checkbox(f"W{week}", value=is_present, key=f"form_att_{student['id']}_{class_id}_{week}")
        
        save_btn = st.form_submit_button("💾 Save All Changes", type="primary", use_container_width=True)
        
        if save_btn:
            # Collect all values from the form and update DB
            updated_count = 0
            for i, student in students.iterrows():
                for week in range(1, 11):
                    key = f"form_att_{student['id']}_{class_id}_{week}"
                    new_val = st.session_state.get(key)
                    old_val = (attendance_lookup.get((student['id'], week)) == 'Present')
                    
                    if new_val != old_val:
                        update_attendance(student['id'], class_id, week, 'Present' if new_val else 'Absent')
                        updated_count += 1
            
            if updated_count > 0:
                st.success(f"Successfully updated {updated_count} attendance records!")
                st.rerun()
            else:
                st.info("No changes were made.")
