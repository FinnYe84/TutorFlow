import sqlite3
import os
import bcrypt

DB_NAME = "tutor_management.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        grade TEXT,
        parent_name TEXT,
        mobile TEXT,
        email TEXT,
        t1_paid BOOLEAN DEFAULT 0,
        t2_paid BOOLEAN DEFAULT 0,
        t3_paid BOOLEAN DEFAULT 0,
        t4_paid BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1
    )
    ''')

    # Teachers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        subject TEXT,
        hourly_rate REAL,
        phone TEXT,
        is_active BOOLEAN DEFAULT 1
    )
    ''')

    # Rooms table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        is_active BOOLEAN DEFAULT 1
    )
    ''')

    # Classes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        day_of_week TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        teacher_id INTEGER,
        room_id INTEGER,
        max_capacity INTEGER,
        term TEXT,
        FOREIGN KEY (teacher_id) REFERENCES Teachers(id),
        FOREIGN KEY (room_id) REFERENCES Rooms(id)
    )
    ''')

    # Enrollments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        class_id INTEGER,
        retention_status TEXT DEFAULT 'Returning',
        FOREIGN KEY (student_id) REFERENCES Students(id),
        FOREIGN KEY (class_id) REFERENCES Classes(id)
    )
    ''')

    # Attendance table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        class_id INTEGER,
        week_number INTEGER,
        status TEXT,
        FOREIGN KEY (student_id) REFERENCES Students(id),
        FOREIGN KEY (class_id) REFERENCES Classes(id)
    )
    ''')

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        teacher_id INTEGER,
        full_name TEXT,
        email TEXT,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (teacher_id) REFERENCES Teachers(id)
    )
    ''')

    # Waitlists table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Waitlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        class_id INTEGER,
        FOREIGN KEY (student_id) REFERENCES Students(id),
        FOREIGN KEY (class_id) REFERENCES Classes(id)
    )
    ''')

    # Academic_Calendar table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Academic_Calendar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term_name TEXT NOT NULL,
        year INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL
    )
    ''')

    # Public_Holidays table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Public_Holidays (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        holiday_date TEXT NOT NULL,
        holiday_name TEXT
    )
    ''')

    # Insert default admin user
    admin_password = "admin_password"
    hashed_pw = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cursor.execute("INSERT INTO Users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)", 
                       ('admin', hashed_pw, 'Admin', 'School Admin'))
    except sqlite3.IntegrityError:
        pass

    # Insert some dummy data for Rooms
    rooms = [('Room 1', 10), ('Room 2', 8), ('Room 3', 12)]
    cursor.executemany("INSERT OR IGNORE INTO Rooms (name, capacity) VALUES (?, ?)", rooms)

    # Insert 2026 Terms
    terms = [
        ('Term 1', 2026, '2026-02-02', '2026-04-02'),
        ('Term 2', 2026, '2026-04-22', '2026-07-03'),
        ('Term 3', 2026, '2026-07-21', '2026-09-25'),
        ('Term 4', 2026, '2026-10-13', '2026-12-17')
    ]
    cursor.executemany("INSERT OR IGNORE INTO Academic_Calendar (term_name, year, start_date, end_date) VALUES (?, ?, ?, ?)", terms)

    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized successfully with admin user and basic data.")

if __name__ == "__main__":
    init_db()
