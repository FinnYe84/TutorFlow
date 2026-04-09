import streamlit as st
import pandas as pd
from database import run_query, run_update

@st.dialog("Edit Term")
def edit_term_dialog(term_id):
    terms_df = run_query("SELECT * FROM Academic_Calendar")
    term_data = terms_df[terms_df['id'] == term_id].iloc[0]
    from datetime import datetime
    curr_start = datetime.strptime(term_data['start_date'], "%Y-%m-%d").date()
    curr_end = datetime.strptime(term_data['end_date'], "%Y-%m-%d").date()
    
    with st.form("edit_term_form_dialog"):
        edit_term_name = st.text_input("Term Name", value=term_data['term_name'])
        edit_year = st.number_input("Year", min_value=2020, value=int(term_data['year']))
        edit_start = st.date_input("Start Date", value=curr_start)
        edit_end = st.date_input("End Date", value=curr_end)
        
        if st.form_submit_button("Update Term"):
            run_update("""
                UPDATE Academic_Calendar 
                SET term_name = :name, year = :year, start_date = :start, end_date = :end 
                WHERE id = :id
            """, {"name": edit_term_name, "year": edit_year, "start": edit_start.strftime("%Y-%m-%d"), "end": edit_end.strftime("%Y-%m-%d"), "id": term_id})
            st.success("Term updated!")
            st.rerun()

@st.dialog("Delete Term")
def delete_term_dialog(term_id, term_name):
    st.warning(f"Are you sure you want to delete **{term_name}**?")
    if st.button("Yes, Delete"):
        run_update("DELETE FROM Academic_Calendar WHERE id = :id", {"id": term_id})
        st.success("Term deleted.")
        st.rerun()

@st.dialog("Edit Holiday")
def edit_holiday_dialog(holiday_id):
    holidays_df = run_query("SELECT * FROM Public_Holidays")
    holiday_data = holidays_df[holidays_df['id'] == holiday_id].iloc[0]
    from datetime import datetime
    curr_holiday_date = datetime.strptime(holiday_data['holiday_date'], "%Y-%m-%d").date()
    
    with st.form("edit_holiday_form_dialog"):
        edit_holiday_name = st.text_input("Holiday Name", value=holiday_data['holiday_name'])
        edit_holiday_date = st.date_input("Holiday Date", value=curr_holiday_date)
        
        if st.form_submit_button("Update Holiday"):
            run_update("""
                UPDATE Public_Holidays 
                SET holiday_name = :name, holiday_date = :date 
                WHERE id = :id
            """, {"name": edit_holiday_name, "date": edit_holiday_date.strftime("%Y-%m-%d"), "id": holiday_id})
            st.success("Holiday updated!")
            st.rerun()

@st.dialog("Delete Holiday")
def delete_holiday_dialog(holiday_id, holiday_name):
    st.warning(f"Are you sure you want to delete **{holiday_name}**?")
    if st.button("Yes, Delete"):
        run_update("DELETE FROM Public_Holidays WHERE id = :id", {"id": holiday_id})
        st.success("Holiday deleted.")
        st.rerun()

def show_settings():
    st.title("School Settings")
    
    tab1, tab2 = st.tabs(["Academic Calendar", "Public Holidays"])
    
    with tab1:
        st.header("Academic Calendar")
        terms_df = run_query("SELECT * FROM Academic_Calendar")
        if not terms_df.empty:
            # Table Header
            hcol1, hcol2, hcol3, hcol4 = st.columns([2, 1, 3, 3])
            hcol1.write("**Term**")
            hcol2.write("**Year**")
            hcol3.write("**Dates**")
            hcol4.write("**Actions**")
            st.divider()
            
            for _, term in terms_df.iterrows():
                rcol1, rcol2, rcol3, rcol4 = st.columns([2, 1, 3, 3])
                rcol1.write(term['term_name'])
                rcol2.write(str(term['year']))
                rcol3.write(f"{term['start_date']} to {term['end_date']}")
                
                with rcol4:
                    acol1, acol2 = st.columns(2)
                    if acol1.button("Modify", key=f"edit_trm_{term['id']}"):
                        edit_term_dialog(term['id'])
                    if acol2.button("Delete", key=f"del_trm_{term['id']}"):
                        delete_term_dialog(term['id'], f"{term['term_name']} {term['year']}")
        else:
            st.info("No terms configured.")
            
        with st.expander("➕ Add New Term"):
            with st.form("add_term_form"):
                term_name = st.text_input("Term Name (e.g. Term 1)")
                year = st.number_input("Year", min_value=2020, value=2026)
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date")
                if st.form_submit_button("Add Term"):
                    run_update("INSERT INTO Academic_Calendar (term_name, year, start_date, end_date) VALUES (:name, :year, :start, :end)", 
                               {"name": term_name, "year": year, "start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")})
                    st.success(f"Added term: {term_name} {year}")
                    st.rerun()
                    
    with tab2:
        st.header("Public Holidays")
        holidays_df = run_query("SELECT * FROM Public_Holidays")
        if not holidays_df.empty:
            # Table Header
            hcol1, hcol2, hcol3 = st.columns([3, 3, 3])
            hcol1.write("**Holiday Name**")
            hcol2.write("**Date**")
            hcol3.write("**Actions**")
            st.divider()
            
            for _, holiday in holidays_df.iterrows():
                rcol1, rcol2, rcol3 = st.columns([3, 3, 3])
                rcol1.write(holiday['holiday_name'])
                rcol2.write(holiday['holiday_date'])
                
                with rcol3:
                    acol1, acol2 = st.columns(2)
                    if acol1.button("Modify", key=f"edit_hld_{holiday['id']}"):
                        edit_holiday_dialog(holiday['id'])
                    if acol2.button("Delete", key=f"del_hld_{holiday['id']}"):
                        delete_holiday_dialog(holiday['id'], holiday['holiday_name'])
        else:
            st.info("No public holidays configured.")
            
        with st.expander("➕ Add Public Holiday"):
            with st.form("add_holiday_form"):
                holiday_name = st.text_input("Holiday Name")
                holiday_date = st.date_input("Holiday Date")
                if st.form_submit_button("Add Holiday"):
                    run_update("INSERT INTO Public_Holidays (holiday_date, holiday_name) VALUES (:date, :name)", 
                               {"date": holiday_date.strftime("%Y-%m-%d"), "name": holiday_name})
                    st.success(f"Added holiday: {holiday_name}")
                    st.rerun()
