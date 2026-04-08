import sqlite3

DB_NAME = "tutor_management.db"

def check_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    tables = ['Students', 'Teachers', 'Rooms', 'Classes']
    for table in tables:
        print(f"--- {table} ---")
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    
    conn.close()

if __name__ == "__main__":
    check_db()
