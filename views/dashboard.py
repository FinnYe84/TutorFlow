import streamlit as st
import pandas as pd
from database import run_query, get_all_classes_for_term, get_enrollment_count, get_students_in_class

def show_dashboard():
    st.title("TutorFlow Master Schedule")
    
    # Term selector
    terms_df = run_query("SELECT * FROM Academic_Calendar")
    term_options = [f"{row['term_name']} {row['year']}" for _, row in terms_df.iterrows()]
    selected_term = st.selectbox("Select Term", term_options)
    
    # Get classes for selected term
    classes = get_all_classes_for_term(selected_term)
    
    if classes.empty:
        st.info("No classes scheduled for this term.")
    else:
        # Create a visual grid
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            st.subheader(day)
            day_classes = classes[classes['day_of_week'] == day]
            
            if day_classes.empty:
                st.write("No classes.")
            else:
                cols = st.columns(len(day_classes))
                for i, (_, cls) in enumerate(day_classes.iterrows()):
                    with cols[i]:
                        count = get_enrollment_count(cls['id'])
                        fill_rate = count / cls['max_capacity']
                        
                        # Color coding based on capacity
                        color = "green"
                        if fill_rate >= 1.0:
                            color = "red"
                        elif fill_rate >= 0.8:
                            color = "orange"
                            
                        # Card-like display
                        st.markdown(f"""
                        <div style="border: 1px solid {color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <h4 style="margin: 0; color: {color};">{cls['subject']}</h4>
                            <p style="margin: 5px 0;">{cls['start_time']} - {cls['end_time']}</p>
                            <p style="margin: 5px 0;">Teacher: {cls['teacher_name']}</p>
                            <p style="margin: 5px 0;">Room: {cls['room_name']}</p>
                            <p style="margin: 5px 0;">Capacity: {count} / {cls['max_capacity']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("👥 View Students", key=f"btn_{cls['id']}"):
                            if st.session_state.get('view_class_id') == cls['id']:
                                del st.session_state['view_class_id']
                            else:
                                st.session_state['view_class_id'] = cls['id']
                            st.rerun()

                        # If this class is selected, show students right under the button
                        if st.session_state.get('view_class_id') == cls['id']:
                            st.markdown("---")
                            st.write("**Student List:**")
                            students = get_students_in_class(cls['id'])
                            if not students.empty:
                                # Show a simplified list for narrow columns
                                for _, student in students.iterrows():
                                    st.write(f"- {student['name']} ({student['grade']})")
                            else:
                                st.write("No students yet.")
                            
                            if st.button("Close", key=f"close_{cls['id']}"):
                                del st.session_state['view_class_id']
                                st.rerun()
