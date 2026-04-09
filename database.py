import streamlit as st
import pandas as pd
import sqlite3
import os

from sqlalchemy import text

# Use SQLite for local development, PostgreSQL (Supabase) for deployment
def get_connection():
    if "connections" in st.secrets and "postgresql" in st.secrets["connections"]:
        # Use st.connection for PostgreSQL
        conn = st.connection("postgresql", type="sql")
        return conn
    else:
        # Fallback to SQLite locally
        DB_NAME = "tutor_management.db"
        return sqlite3.connect(DB_NAME)

def run_query(query, params=None):
    if params is None:
        params = {}
    conn = get_connection()
    if isinstance(conn, sqlite3.Connection):
        # SQLite works with ? but if we use named params (:name) it also works.
        # We'll stick to what the caller provides.
        return pd.read_sql_query(query, conn, params=params)
    else:
        # st.connection (PostgreSQL)
        # 1. Convert ? to :p0, :p1 etc if params is a list/tuple
        if isinstance(params, (list, tuple)):
            new_query = query
            new_params = {}
            for i, val in enumerate(params):
                placeholder = f":p{i}"
                # Replace ONLY the first '?' found
                new_query = new_query.replace("?", placeholder, 1)
                new_params[f"p{i}"] = val
            query = new_query
            params = new_params
        
        # 2. DO NOT use text() here, it causes UnhashableParamError in Streamlit's cache
        return conn.query(query, params=params, ttl=0)

def run_update(query, params=None):
    if params is None:
        params = {}
    conn = get_connection()
    if isinstance(conn, sqlite3.Connection):
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid
    else:
        # st.connection (PostgreSQL)
        if isinstance(params, (list, tuple)):
            new_query = query
            new_params = {}
            for i, val in enumerate(params):
                placeholder = f":p{i}"
                new_query = new_query.replace("?", placeholder, 1)
                new_params[f"p{i}"] = val
            query = new_query
            params = new_params
            
        with conn.session as s:
            s.execute(text(query), params)
            s.commit()
            return None

def get_all_students(only_active=False):
    if only_active:
        # Use boolean literal for PostgreSQL compatibility
        return run_query("SELECT * FROM Students WHERE is_active = TRUE")
    return run_query("SELECT * FROM Students")

def get_all_teachers(only_active=False):
    if only_active:
        return run_query("SELECT * FROM Teachers WHERE is_active = TRUE")
    return run_query("SELECT * FROM Teachers")

def get_all_rooms(only_active=False):
    if only_active:
        return run_query("SELECT * FROM Rooms WHERE is_active = TRUE")
    return run_query("SELECT * FROM Rooms")

def set_active_status(table, entity_id, status):
    # Valid tables: Students, Teachers, Rooms, Users
    # PostgreSQL handles Python booleans (True/False) correctly as BOOLEAN types
    query = f"UPDATE {table} SET is_active = :status WHERE id = :id"
    run_update(query, {"status": status, "id": entity_id})
    
    # Smart cleanup if deactivating
    if not status:
        if table == 'Students':
            # Remove from all current enrollments and waitlists
            run_update("DELETE FROM Enrollments WHERE student_id = :id", {"id": entity_id})
            run_update("DELETE FROM Waitlists WHERE student_id = :id", {"id": entity_id})
        elif table == 'Teachers':
            # Set teacher_id to NULL in Classes
            run_update("UPDATE Classes SET teacher_id = NULL WHERE teacher_id = :id", {"id": entity_id})
            # Also update the corresponding User account if it exists
            run_update("UPDATE Users SET is_active = FALSE WHERE teacher_id = :id", {"id": entity_id})
        elif table == 'Rooms':
            # Set room_id to NULL in Classes
            run_update("UPDATE Classes SET room_id = NULL WHERE room_id = :id", {"id": entity_id})
    elif status and table == 'Teachers':
        # If reactivating a teacher, reactivate their user account too
        run_update("UPDATE Users SET is_active = TRUE WHERE teacher_id = :id", {"id": entity_id})

def delete_entity(table, entity_id):
    # Check for dependencies first (simplified)
    if table == 'Students':
        run_update("DELETE FROM Enrollments WHERE student_id = :id", {"id": entity_id})
        run_update("DELETE FROM Attendance WHERE student_id = :id", {"id": entity_id})
        run_update("DELETE FROM Waitlists WHERE student_id = :id", {"id": entity_id})
    elif table == 'Teachers':
        run_update("UPDATE Classes SET teacher_id = NULL WHERE teacher_id = :id", {"id": entity_id})
        run_update("DELETE FROM Users WHERE teacher_id = :id", {"id": entity_id})
    elif table == 'Rooms':
        run_update("UPDATE Classes SET room_id = NULL WHERE room_id = :id", {"id": entity_id})
    
    run_update(f"DELETE FROM {table} WHERE id = :id", {"id": entity_id})

def get_all_classes():
    query = """
    SELECT c.*, t.name as teacher_name, r.name as room_name 
    FROM Classes c
    LEFT JOIN Teachers t ON c.teacher_id = t.id
    LEFT JOIN Rooms r ON c.room_id = r.id
    """
    return run_query(query)

def get_all_classes_for_term(term):
    query = """
    SELECT c.*, t.name as teacher_name, r.name as room_name 
    FROM Classes c
    LEFT JOIN Teachers t ON c.teacher_id = t.id
    LEFT JOIN Rooms r ON c.room_id = r.id
    WHERE c.term = :term
    """
    return run_query(query, {"term": term})

def get_enrollment_count(class_id):
    query = "SELECT count(*) as count FROM Enrollments WHERE class_id = :id"
    res = run_query(query, {"id": class_id})
    return res.iloc[0]['count']

def get_attendance(student_id, class_id, week_number):
    query = "SELECT status FROM Attendance WHERE student_id = :sid AND class_id = :cid AND week_number = :wn"
    res = run_query(query, {"sid": student_id, "cid": class_id, "wn": week_number})
    if not res.empty:
        return res.iloc[0]['status']
    return None

def update_attendance(student_id, class_id, week_number, status):
    # Check if record exists
    existing = get_attendance(student_id, class_id, week_number)
    if existing is not None:
        run_update("UPDATE Attendance SET status = :status WHERE student_id = :sid AND class_id = :cid AND week_number = :wn", 
                   {"status": status, "sid": student_id, "cid": class_id, "wn": week_number})
    else:
        run_update("INSERT INTO Attendance (student_id, class_id, week_number, status) VALUES (:sid, :cid, :wn, :status)", 
                   {"sid": student_id, "cid": class_id, "wn": week_number, "status": status})

def get_classes_for_teacher(teacher_id):
    query = """
    SELECT c.*, r.name as room_name 
    FROM Classes c
    LEFT JOIN Rooms r ON c.room_id = r.id
    WHERE c.teacher_id = :id
    """
    return run_query(query, {"id": teacher_id})

def check_overlaps(day_of_week, start_time, end_time, teacher_id, room_id, term, exclude_class_id=None):
    # This checks for overlaps within the same term
    params = {
        "dow": day_of_week, 
        "term": term, 
        "tid": teacher_id, 
        "rid": room_id, 
        "st": start_time, 
        "et": end_time
    }
    
    teacher_query = """
        SELECT id FROM Classes 
        WHERE day_of_week = :dow AND term = :term AND teacher_id = :tid
        AND ((start_time <= :st AND end_time > :st) OR (start_time < :et AND end_time >= :et) OR (:st <= start_time AND :et >= end_time))
    """
    if exclude_class_id:
        teacher_query += " AND id != :ex_id"
        params["ex_id"] = exclude_class_id
    teacher_conflict = not run_query(teacher_query, params).empty
    
    room_query = """
        SELECT id FROM Classes 
        WHERE day_of_week = :dow AND term = :term AND room_id = :rid
        AND ((start_time <= :st AND end_time > :st) OR (start_time < :et AND end_time >= :et) OR (:st <= start_time AND :et >= end_time))
    """
    if exclude_class_id:
        room_query += " AND id != :ex_id"
        params["ex_id"] = exclude_class_id
    room_conflict = not run_query(room_query, params).empty
    
    return teacher_conflict, room_conflict

def get_class_details(class_id):
    query = """
    SELECT c.*, t.name as teacher_name, r.name as room_name 
    FROM Classes c
    LEFT JOIN Teachers t ON c.teacher_id = t.id
    LEFT JOIN Rooms r ON c.room_id = r.id
    WHERE c.id = :id
    """
    return run_query(query, {"id": class_id})

def get_students_in_class(class_id):
    query = """
    SELECT s.*, e.retention_status
    FROM Students s
    JOIN Enrollments e ON s.id = e.student_id
    WHERE e.class_id = :id
    """
    return run_query(query, {"id": class_id})

def get_waitlist_for_class(class_id):
    query = """
    SELECT s.*
    FROM Students s
    JOIN Waitlists w ON s.id = w.student_id
    WHERE w.class_id = :id
    """
    return run_query(query, {"id": class_id})

def get_user_by_username(username):
    # Use LOWER() for case-insensitive username lookup in PostgreSQL
    query = "SELECT * FROM Users WHERE LOWER(username) = LOWER(:un)"
    res = run_query(query, {"un": username})
    if not res.empty:
        # Convert the first row to a dictionary
        return res.iloc[0].to_dict()
    return None

def update_user_password(user_id, new_hashed_password):
    query = "UPDATE Users SET password_hash = :pw WHERE id = :id"
    run_update(query, {"pw": new_hashed_password, "id": user_id})

def reset_teacher_password(teacher_id, new_hashed_password):
    query = "UPDATE Users SET password_hash = :pw WHERE teacher_id = :tid"
    run_update(query, {"pw": new_hashed_password, "tid": teacher_id})
