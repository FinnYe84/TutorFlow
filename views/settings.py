import streamlit as st
import pandas as pd
from database import run_query, run_update

def show_settings():
    st.title("School Settings")
    
    tab1, tab2 = st.tabs(["Academic Calendar", "Public Holidays"])
    
    with tab1:
        st.header("Academic Calendar")
        terms_df = run_query("SELECT * FROM Academic_Calendar")
        if not terms_df.empty:
            st.dataframe(terms_df)
            
            st.subheader("Manage Term")
            term_to_manage = st.selectbox("Select Term to Edit/Delete", 
                                           options=terms_df['id'].tolist(),
                                           format_func=lambda x: f"{terms_df[terms_df['id'] == x]['term_name'].values[0]} {terms_df[terms_df['id'] == x]['year'].values[0]}")
            
            if st.button("🗑️ Delete Term", key="delete_term_btn"):
                run_update("DELETE FROM Academic_Calendar WHERE id = :id", {"id": term_to_manage})
                st.success("Term deleted.")
                st.rerun()
            
            with st.expander("📝 Edit Term Details"):
                term_data = terms_df[terms_df['id'] == term_to_manage].iloc[0]
                from datetime import datetime
                curr_start = datetime.strptime(term_data['start_date'], "%Y-%m-%d").date()
                curr_end = datetime.strptime(term_data['end_date'], "%Y-%m-%d").date()
                
                with st.form("edit_term_form"):
                    edit_term_name = st.text_input("Term Name", value=term_data['term_name'])
                    edit_year = st.number_input("Year", min_value=2020, value=int(term_data['year']))
                    edit_start = st.date_input("Start Date", value=curr_start)
                    edit_end = st.date_input("End Date", value=curr_end)
                    
                    if st.form_submit_button("Update Term"):
                        run_update("""
                            UPDATE Academic_Calendar 
                            SET term_name = :name, year = :year, start_date = :start, end_date = :end 
                            WHERE id = :id
                        """, {"name": edit_term_name, "year": edit_year, "start": edit_start.strftime("%Y-%m-%d"), "end": edit_end.strftime("%Y-%m-%d"), "id": term_to_manage})
                        st.success("Term updated successfully!")
                        st.rerun()
        else:
            st.info("No terms configured.")
            
        with st.expander("Add New Term"):
            with st.form("add_term_form"):
                term_name = st.text_input("Term Name (e.g. Term 1)")
                year = st.number_input("Year", min_value=2020, value=2026)
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
                submitted = st.form_submit_button("Add Term")
                
                if submitted:
                    run_update("INSERT INTO Academic_Calendar (term_name, year, start_date, end_date) VALUES (:name, :year, :start, :end)", 
                               {"name": term_name, "year": year, "start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")})
                    st.success(f"Added term: {term_name} {year}")
                    st.rerun()
                    
    with tab2:
        st.header("Public Holidays")
        holidays_df = run_query("SELECT * FROM Public_Holidays")
        if not holidays_df.empty:
            st.dataframe(holidays_df)
            
            st.subheader("Manage Holiday")
            holiday_to_manage = st.selectbox("Select Holiday to Edit/Delete", 
                                              options=holidays_df['id'].tolist(),
                                              format_func=lambda x: f"{holidays_df[holidays_df['id'] == x]['holiday_name'].values[0]} ({holidays_df[holidays_df['id'] == x]['holiday_date'].values[0]})")
            
            if st.button("🗑️ Delete Holiday", key="delete_holiday_btn"):
                run_update("DELETE FROM Public_Holidays WHERE id = :id", {"id": holiday_to_manage})
                st.success("Holiday deleted.")
                st.rerun()
            
            with st.expander("📝 Edit Holiday Details"):
                holiday_data = holidays_df[holidays_df['id'] == holiday_to_manage].iloc[0]
                from datetime import datetime
                curr_holiday_date = datetime.strptime(holiday_data['holiday_date'], "%Y-%m-%d").date()
                
                with st.form("edit_holiday_form"):
                    edit_holiday_name = st.text_input("Holiday Name", value=holiday_data['holiday_name'])
                    edit_holiday_date = st.date_input("Holiday Date", value=curr_holiday_date)
                    
                    if st.form_submit_button("Update Holiday"):
                        run_update("""
                            UPDATE Public_Holidays 
                            SET holiday_name = :name, holiday_date = :date 
                            WHERE id = :id
                        """, {"name": edit_holiday_name, "date": edit_holiday_date.strftime("%Y-%m-%d"), "id": holiday_to_manage})
                        st.success("Holiday updated successfully!")
                        st.rerun()
        else:
            st.info("No public holidays configured.")
            
        with st.expander("Add Public Holiday"):
            with st.form("add_holiday_form"):
                holiday_name = st.text_input("Holiday Name")
                holiday_date = st.date_input("Holiday Date")
                submitted = st.form_submit_button("Add Holiday")
                
                if submitted:
                    run_update("INSERT INTO Public_Holidays (holiday_date, holiday_name) VALUES (:date, :name)", 
                               {"date": holiday_date.strftime("%Y-%m-%d"), "name": holiday_name})
                    st.success(f"Added holiday: {holiday_name}")
                    st.rerun()
