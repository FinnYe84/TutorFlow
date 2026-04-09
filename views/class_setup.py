import streamlit as st
import pandas as pd
from database import run_query, run_update, get_all_teachers, get_all_rooms, get_all_classes, check_overlaps, get_all_students

def show_class_setup():
    st.title("Class Arrangement & Management")
    
    tab1, tab2 = st.tabs(["Manage Classes", "Enroll Students"])
    
    with tab1:
        st.header("Existing Classes")
        df_classes = get_all_classes()
        if not df_classes.empty:
            st.dataframe(df_classes)
            
            st.subheader("Class Actions")
            class_to_manage = st.selectbox("Select Class to Manage", 
                                            options=df_classes['id'].tolist(),
                                            format_func=lambda x: f"{df_classes[df_classes['id'] == x]['subject'].values[0]} ({df_classes[df_classes['id'] == x]['day_of_week'].values[0]} {df_classes[df_classes['id'] == x]['start_time'].values[0]})")
            
            if st.button("🗑️ Delete Class", key="delete_class_btn"):
                # Clean up enrollments and waitlists first
                run_update("DELETE FROM Enrollments WHERE class_id = :id", {"id": class_to_manage})
                run_update("DELETE FROM Waitlists WHERE class_id = :id", {"id": class_to_manage})
                run_update("DELETE FROM Attendance WHERE class_id = :id", {"id": class_to_manage})
                run_update("DELETE FROM Classes WHERE id = :id", {"id": class_to_manage})
                st.success("Class deleted successfully.")
                st.rerun()
            
            with st.expander("📝 Edit Class Details"):
                cls_data = df_classes[df_classes['id'] == class_to_manage].iloc[0]
                
                with st.form("edit_class_form"):
                    edit_subject = st.text_input("Subject", value=cls_data['subject'])
                    edit_day = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], 
                                            index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(cls_data['day_of_week']))
                    
                    # Convert time strings to time objects
                    from datetime import datetime
                    curr_start = datetime.strptime(cls_data['start_time'], "%H:%M").time()
                    curr_end = datetime.strptime(cls_data['end_time'], "%H:%M").time()
                    
                    edit_start = st.time_input("Start Time", value=curr_start)
                    edit_end = st.time_input("End Time", value=curr_end)
                    
                    # Only show active teachers and rooms
                    teachers_edit = get_all_teachers(only_active=True)
                    teacher_options_edit = {row['name']: row['id'] for _, row in teachers_edit.iterrows()}
                    # If current teacher is inactive, we still need them in the list or handle it
                    curr_teacher_name = cls_data['teacher_name'] if pd.notna(cls_data['teacher_name']) else "None"
                    if curr_teacher_name not in teacher_options_edit and pd.notna(cls_data['teacher_id']):
                         teacher_options_edit[curr_teacher_name] = int(cls_data['teacher_id'])
                    
                    edit_teacher = st.selectbox("Teacher", list(teacher_options_edit.keys()), 
                                                index=list(teacher_options_edit.keys()).index(curr_teacher_name) if curr_teacher_name in teacher_options_edit else 0)
                    
                    rooms_edit = get_all_rooms(only_active=True)
                    room_data_edit = {row['name']: (row['id'], row['capacity']) for _, row in rooms_edit.iterrows()}
                    curr_room_name = cls_data['room_name'] if pd.notna(cls_data['room_name']) else "None"
                    if curr_room_name not in room_data_edit and pd.notna(cls_data['room_id']):
                        # We don't have the capacity for an inactive room easily here, but let's assume it's large enough or handle it
                        room_data_edit[curr_room_name] = (int(cls_data['room_id']), 999) 
                    
                    edit_room = st.selectbox("Room", list(room_data_edit.keys()), 
                                             index=list(room_data_edit.keys()).index(curr_room_name) if curr_room_name in room_data_edit else 0)
                    
                    if edit_room:
                        st.info(f"Selected room capacity: {room_data_edit[edit_room][1]}")
                    
                    edit_max_cap = st.number_input("Max Capacity", min_value=1, value=int(cls_data['max_capacity']))
                    
                    terms_df_edit = run_query("SELECT * FROM Academic_Calendar")
                    term_options_edit = [f"{row['term_name']} {row['year']}" for _, row in terms_df_edit.iterrows()]
                    curr_term = cls_data['term']
                    edit_term = st.selectbox("Term", term_options_edit, 
                                             index=term_options_edit.index(curr_term) if curr_term in term_options_edit else 0)
                    
                    if st.form_submit_button("Update Class"):
                        start_str_edit = edit_start.strftime("%H:%M")
                        end_str_edit = edit_end.strftime("%H:%M")
                        teacher_id_edit = teacher_options_edit[edit_teacher]
                        room_id_edit, room_cap_edit = room_data_edit[edit_room]
                        
                        if edit_max_cap > room_cap_edit:
                            st.error(f"Class capacity ({edit_max_cap}) cannot exceed room capacity ({room_cap_edit})!")
                        else:
                            # Use the updated check_overlaps with exclude_class_id
                            t_conf, r_conf = check_overlaps(edit_day, start_str_edit, end_str_edit, teacher_id_edit, room_id_edit, edit_term, exclude_class_id=class_to_manage)
                            
                            if t_conf:
                                st.error("Teacher already has a class during this time!")
                            elif r_conf:
                                st.error("Room is already occupied during this time!")
                            else:
                                run_update("""
                                    UPDATE Classes 
                                    SET subject = :subject, day_of_week = :dow, start_time = :start, 
                                        end_time = :end, teacher_id = :tid, room_id = :rid, 
                                        max_capacity = :cap, term = :term 
                                    WHERE id = :id
                                """, {"subject": edit_subject, "dow": edit_day, "start": start_str_edit, 
                                      "end": end_str_edit, "tid": teacher_id_edit, "rid": room_id_edit, 
                                      "cap": edit_max_cap, "term": edit_term, "id": class_to_manage})
                                st.success("Class updated successfully!")
                                st.rerun()
        else:
            st.info("No classes found.")
        
        with st.expander("Create New Class"):
            with st.form("create_class_form"):
                subject = st.text_input("Subject")
                day_of_week = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")
                
                # Only show active teachers and rooms
                teachers = get_all_teachers(only_active=True)
                teacher_options = {row['name']: row['id'] for _, row in teachers.iterrows()}
                teacher_name = st.selectbox("Teacher", list(teacher_options.keys()))
                
                rooms = get_all_rooms(only_active=True)
                # Map room names to their ID and capacity
                room_data = {row['name']: (row['id'], row['capacity']) for _, row in rooms.iterrows()}
                room_name = st.selectbox("Room", list(room_data.keys()))
                
                # Validation will be checked on submit, but we can hint at the room capacity
                if room_name:
                    st.info(f"Selected room capacity: {room_data[room_name][1]}")
                
                max_capacity = st.number_input("Max Capacity", min_value=1, value=10)
                
                # Fetch available terms
                terms_df = run_query("SELECT * FROM Academic_Calendar")
                term_options = [f"{row['term_name']} {row['year']}" for _, row in terms_df.iterrows()]
                term = st.selectbox("Term", term_options)
                
                submitted = st.form_submit_button("Create Class")
                
                if submitted:
                    start_str = start_time.strftime("%H:%M")
                    end_str = end_time.strftime("%H:%M")
                    teacher_id = teacher_options[teacher_name]
                    room_id, room_capacity = room_data[room_name]
                    
                    # New Validation: Class capacity cannot exceed room capacity
                    if max_capacity > room_capacity:
                        st.error(f"Class capacity ({max_capacity}) cannot exceed room capacity ({room_capacity}) for {room_name}!")
                    else:
                        # Automated Conflict Validation
                        teacher_conflict, room_conflict = check_overlaps(day_of_week, start_str, end_str, teacher_id, room_id, term)
                        
                        if teacher_conflict:
                            st.error(f"Teacher {teacher_name} already has a class during this time!")
                        elif room_conflict:
                            st.error(f"Room {room_name} is already occupied during this time!")
                        else:
                            run_update("""
                                INSERT INTO Classes (subject, day_of_week, start_time, end_time, teacher_id, room_id, max_capacity, term)
                                VALUES (:subject, :dow, :start, :end, :tid, :rid, :cap, :term)
                            """, {"subject": subject, "dow": day_of_week, "start": start_str, "end": end_str, "tid": teacher_id, "rid": room_id, "cap": max_capacity, "term": term})
                            st.success(f"Class '{subject}' created successfully.")
                            st.rerun()

    with tab2:
        st.header("Enroll Students")
        df_classes = get_all_classes()
        if df_classes.empty:
            st.warning("Please create a class first.")
        else:
            class_options = {f"{row['subject']} ({row['day_of_week']} {row['start_time']} - {row['end_time']})": row['id'] for _, row in df_classes.iterrows()}
            selected_class_label = st.selectbox("Select Class", list(class_options.keys()))
            class_id = class_options[selected_class_label]
            
            # Show current enrollment fill rate
            enrollments = run_query("SELECT count(*) as count FROM Enrollments WHERE class_id = ?", (class_id,))
            current_count = enrollments.iloc[0]['count']
            max_cap = df_classes[df_classes['id'] == class_id]['max_capacity'].values[0]
            
            st.write(f"**Fill Rate:** {current_count} / {max_cap}")
            
            # Student search and enroll (only active students)
            students = get_all_students(only_active=True)
            student_options = {row['name']: row['id'] for _, row in students.iterrows()}
            student_name = st.selectbox("Select Student", list(student_options.keys()))
            student_id = student_options[student_name]
            
            # Check if student already enrolled
            already_enrolled = run_query("SELECT id FROM Enrollments WHERE student_id = ? AND class_id = ?", (student_id, class_id))
            
            if not already_enrolled.empty:
                st.info(f"{student_name} is already enrolled in this class.")
            else:
                if st.button("Enroll Student"):
                    if current_count < max_cap:
                        run_update("INSERT INTO Enrollments (student_id, class_id) VALUES (:sid, :cid)", {"sid": student_id, "cid": class_id})
                        st.success(f"Enrolled {student_name} in {selected_class_label}")
                        st.rerun()
                    else:
                        st.warning("Class is full! Adding to Waitlist.")
                        run_update("INSERT INTO Waitlists (student_id, class_id) VALUES (:sid, :cid)", {"sid": student_id, "cid": class_id})
                        st.success(f"Added {student_name} to Waitlist.")
                        st.rerun()
