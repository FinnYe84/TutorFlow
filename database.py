import sqlite3
import pandas as pd

DB_NAME = "tutor_management.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def run_query(query, params=()):
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)

def run_update(query, params=()):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid

def get_all_students(only_active=False):
    if only_active:
        return run_query("SELECT * FROM Students WHERE is_active = 1")
    return run_query("SELECT * FROM Students")

def get_all_teachers(only_active=False):
    if only_active:
        return run_query("SELECT * FROM Teachers WHERE is_active = 1")
    return run_query("SELECT * FROM Teachers")

def get_all_rooms(only_active=False):
    if only_active:
        return run_query("SELECT * FROM Rooms WHERE is_active = 1")
    return run_query("SELECT * FROM Rooms")

def set_active_status(table, entity_id, status):
    # Valid tables: Students, Teachers, Rooms, Users
    query = f"UPDATE {table} SET is_active = ? WHERE id = ?"
    run_update(query, (1 if status else 0, entity_id))
    
    # Smart cleanup if deactivating
    if not status:
        if table == 'Students':
            # Remove from all current enrollments and waitlists
            run_update("DELETE FROM Enrollments WHERE student_id = ?", (entity_id,))
            run_update("DELETE FROM Waitlists WHERE student_id = ?", (entity_id,))
        elif table == 'Teachers':
            # Set teacher_id to NULL in Classes
            run_update("UPDATE Classes SET teacher_id = NULL WHERE teacher_id = ?", (entity_id,))
            # Also update the corresponding User account if it exists
            run_update("UPDATE Users SET is_active = 0 WHERE teacher_id = ?", (entity_id,))
        elif table == 'Rooms':
            # Set room_id to NULL in Classes
            run_update("UPDATE Classes SET room_id = NULL WHERE room_id = ?", (entity_id,))
    elif status and table == 'Teachers':
        # If reactivating a teacher, reactivate their user account too
        run_update("UPDATE Users SET is_active = 1 WHERE teacher_id = ?", (entity_id,))

def delete_entity(table, entity_id):
    # Check for dependencies first (simplified)
    if table == 'Students':
        run_update("DELETE FROM Enrollments WHERE student_id = ?", (entity_id,))
        run_update("DELETE FROM Attendance WHERE student_id = ?", (entity_id,))
        run_update("DELETE FROM Waitlists WHERE student_id = ?", (entity_id,))
    elif table == 'Teachers':
        # Don't delete teacher if they have classes? Or just set teacher_id to NULL?
        # Let's set teacher_id to NULL in Classes
        run_update("UPDATE Classes SET teacher_id = NULL WHERE teacher_id = ?", (entity_id,))
        run_update("DELETE FROM Users WHERE teacher_id = ?", (entity_id,))
    elif table == 'Rooms':
        run_update("UPDATE Classes SET room_id = NULL WHERE room_id = ?", (entity_id,))
    
    run_update(f"DELETE FROM {table} WHERE id = ?", (entity_id,))

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
    WHERE c.term = ?
    """
    return run_query(query, (term,))

def get_enrollment_count(class_id):
    query = "SELECT count(*) as count FROM Enrollments WHERE class_id = ?"
    return run_query(query, (class_id,)).iloc[0]['count']

def get_attendance(student_id, class_id, week_number):
    query = "SELECT status FROM Attendance WHERE student_id = ? AND class_id = ? AND week_number = ?"
    res = run_query(query, (student_id, class_id, week_number))
    if not res.empty:
        return res.iloc[0]['status']
    return None

def update_attendance(student_id, class_id, week_number, status):
    # Check if record exists
    existing = get_attendance(student_id, class_id, week_number)
    if existing is not None:
        run_update("UPDATE Attendance SET status = ? WHERE student_id = ? AND class_id = ? AND week_number = ?", 
                   (status, student_id, class_id, week_number))
    else:
        run_update("INSERT INTO Attendance (student_id, class_id, week_number, status) VALUES (?, ?, ?, ?)", 
                   (student_id, class_id, week_number, status))

def get_classes_for_teacher(teacher_id):
    query = """
    SELECT c.*, r.name as room_name 
    FROM Classes c
    LEFT JOIN Rooms r ON c.room_id = r.id
    WHERE c.teacher_id = ?
    """
    return run_query(query, (teacher_id,))

def check_overlaps(day_of_week, start_time, end_time, teacher_id, room_id, term):
    # This checks for overlaps within the same term
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Check teacher overlap
        cursor.execute("""
            SELECT id FROM Classes 
            WHERE day_of_week = ? AND term = ? AND teacher_id = ?
            AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?) OR (? <= start_time AND ? >= end_time))
        """, (day_of_week, term, teacher_id, start_time, start_time, end_time, end_time, start_time, end_time))
        
        teacher_conflict = cursor.fetchone()
        
        # Check room overlap
        cursor.execute("""
            SELECT id FROM Classes 
            WHERE day_of_week = ? AND term = ? AND room_id = ?
            AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?) OR (? <= start_time AND ? >= end_time))
        """, (day_of_week, term, room_id, start_time, start_time, end_time, end_time, start_time, end_time))
        
        room_conflict = cursor.fetchone()
        
        return teacher_conflict, room_conflict

def get_class_details(class_id):
    query = """
    SELECT c.*, t.name as teacher_name, r.name as room_name 
    FROM Classes c
    LEFT JOIN Teachers t ON c.teacher_id = t.id
    LEFT JOIN Rooms r ON c.room_id = r.id
    WHERE c.id = ?
    """
    return run_query(query, (class_id,))

def get_students_in_class(class_id):
    query = """
    SELECT s.*, e.retention_status
    FROM Students s
    JOIN Enrollments e ON s.id = e.student_id
    WHERE e.class_id = ?
    """
    return run_query(query, (class_id,))

def get_waitlist_for_class(class_id):
    query = """
    SELECT s.*
    FROM Students s
    JOIN Waitlists w ON s.id = w.student_id
    WHERE w.class_id = ?
    """
    return run_query(query, (class_id,))

def get_user_by_username(username):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, user))
        return None
