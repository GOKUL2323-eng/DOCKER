import sqlite3
import os
import sys
from datetime import datetime

# Try to load environment variables from backend/.env
try:
    from dotenv import load_dotenv
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", ".env"))
    if os.path.exists(env_path):
        load_dotenv(env_path)
except ImportError:
    pass

# Determine database path
database_url = os.getenv("DATABASE_URL")
if database_url:
    if ":///" in database_url:
        DB_PATH = database_url.split(":///", 1)[1]
    elif "://" in database_url:
        DB_PATH = database_url.split("://", 1)[1]
    else:
        DB_PATH = database_url
    
    # Resolve relative path if not absolute
    if not os.path.isabs(DB_PATH) and not DB_PATH.startswith("/") and not DB_PATH.startswith("\\"):
        DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", DB_PATH))
else:
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "shadow_ai.db"))

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    print("\n" + "="*60)
    print(f" {text:^58} ")
    print("="*60)

def get_db_connection():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return None
    try:
        return sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def show_stats():
    conn = get_db_connection()
    if not conn: return
    
    cursor = conn.cursor()
    print_header("SHADOW AI - DATABASE STATISTICS")
    
    tables = {
        "users": "Total Users",
        "chat_sessions": "Total Chat Sessions",
        "messages": "Total Messages"
    }
    
    for table, label in tables.items():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"- {label:<25}: {count}")
        except:
            print(f"- {label:<25}: Table not found")
            
    conn.close()

def list_recent_users():
    conn = get_db_connection()
    if not conn: return
    
    cursor = conn.cursor()
    print_header("RECENT USERS")
    try:
        cursor.execute("SELECT id, username, email, created_at FROM users ORDER BY created_at DESC LIMIT 10")
        users = cursor.fetchall()
        print(f"{'Username':<20} | {'Email':<30} | {'Created At'}")
        print("-" * 75)
        for u in users:
            print(f"{u[1]:<20} | {u[2]:<30} | {u[3]}")
    except Exception as e:
        print(f"Error: {e}")
    conn.close()

def list_recent_sessions():
    conn = get_db_connection()
    if not conn: return
    
    cursor = conn.cursor()
    print_header("RECENT CHAT SESSIONS")
    try:
        cursor.execute("""
            SELECT s.id, u.username, s.title, s.created_at 
            FROM chat_sessions s 
            JOIN users u ON s.user_id = u.id 
            ORDER BY s.created_at DESC LIMIT 10
        """)
        sessions = cursor.fetchall()
        print(f"{'User':<15} | {'Session Title':<35} | {'Date'}")
        print("-" * 75)
        for s in sessions:
            title = (s[2][:32] + '...') if len(s[2]) > 35 else s[2]
            print(f"{s[1]:<15} | {title:<35} | {s[3][:19]}")
    except Exception as e:
        print(f"Error: {e}")
    conn.close()

def main_menu():
    while True:
        clear_screen()
        print_header("SHADOW AI - DATABASE INSPECTOR")
        print("1. View General Statistics")
        print("2. List Recent Users")
        print("3. List Recent Chat Sessions")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ")
        
        if choice == '1':
            show_stats()
            input("\nPress Enter to return to menu...")
        elif choice == '2':
            list_recent_users()
            input("\nPress Enter to return to menu...")
        elif choice == '3':
            list_recent_sessions()
            input("\nPress Enter to return to menu...")
        elif choice == '4':
            print("Exiting inspector...")
            break
        else:
            print("Invalid choice. Try again.")
            import time
            time.sleep(1)

if __name__ == "__main__":
    if not os.path.exists("backend"):
        print("Error: This script must be run from the root directory of the shadow-ai project.")
        sys.exit(1)
    main_menu()
