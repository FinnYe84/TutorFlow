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
