import sqlite3
import os

DB_PATH = "ai_assistant.db"

def add_role_column():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. Running init_db handles creation.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "role" not in columns:
            print("Adding 'role' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
            conn.commit()
            print("Column added successfully.")
            
            # Update existing users to have 'user' role (handled by DEFAULT but good to be explicit if needed)
            # cursor.execute("UPDATE users SET role = 'user' WHERE role IS NULL")
            # conn.commit()
        else:
            print("'role' column already exists.")
            
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_role_column()
