import streamlit as st
import pandas as pd
from database import run_query, get_classes_for_teacher, get_all_classes, get_students_in_class, update_attendance, get_attendance

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
    
    # Create attendance grid
    for i, student in students.iterrows():
        st.subheader(student['name'])
        cols = st.columns(10)
        for week in range(1, 11):
            with cols[week-1]:
                current_status = get_attendance(student['id'], class_id, week)
                is_present = (current_status == 'Present')
                
                new_status = st.checkbox(f"W{week}", value=is_present, key=f"att_{student['id']}_{class_id}_{week}")
                
                # Update DB if changed
                if new_status != is_present:
                    update_attendance(student['id'], class_id, week, 'Present' if new_status else 'Absent')
                    st.toast(f"Updated {student['name']} Week {week}")
