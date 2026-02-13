import sqlite3
import sys

DB_PATH = "ai_assistant.db"

def promote_user(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE users SET role = 'admin' WHERE username = ?", (username,))
        if cursor.rowcount > 0:
            print(f"User '{username}' promoted to admin.")
            conn.commit()
        else:
            print(f"User '{username}' not found.")
            
    except Exception as e:
        print(f"Error promoting user: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promote_user.py <username>")
    else:
        promote_user(sys.argv[1])
