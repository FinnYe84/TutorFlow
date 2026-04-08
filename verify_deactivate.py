import sqlite3

def verify():
    conn = sqlite3.connect('tutor_management.db')
    cursor = conn.cursor()
    
    print("--- Students ---")
    cursor.execute("SELECT id, name, is_active FROM Students")
    students = cursor.fetchall()
    for s in students:
        print(s)
        
    print("\n--- Enrollments ---")
    cursor.execute("SELECT * FROM Enrollments")
    enrollments = cursor.fetchall()
    for e in enrollments:
        print(e)
        
    conn.close()

if __name__ == "__main__":
    verify()
