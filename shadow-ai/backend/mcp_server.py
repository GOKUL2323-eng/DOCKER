import os
import sqlite3
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Shadow AI Server")

# Database path derived from environment or fallback
db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///shadow_ai.db")
if ":///" in db_url:
    DB_PATH = db_url.split(":///", 1)[1]
elif "://" in db_url:
    DB_PATH = db_url.split("://", 1)[1]
else:
    DB_PATH = db_url

if not os.path.isabs(DB_PATH) and not DB_PATH.startswith("/") and not DB_PATH.startswith("\\"):
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), DB_PATH))

@mcp.tool()
def query_shadow_db(sql_query: str):
    """
    Execute a read-only SQL query against the Shadow AI database.
    Use this to retrieve chat history, user sessions, or metadata.
    """
    if not sql_query.strip().lower().startswith("select"):
        return "Error: Only SELECT queries are allowed for safety."
        
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        if not rows:
            return "No data found."
            
        # Convert rows to list of dicts for clean output
        result = [dict(row) for row in rows]
        conn.close()
        return result
    except Exception as e:
        return f"Database Error: {str(e)}"

@mcp.tool()
def get_user_sessions(user_id: str = "guest-user"):
    """
    Retrieve all chat sessions for a specific user.
    """
    query = f"SELECT id, title, created_at, updated_at FROM chat_sessions WHERE user_id = '{user_id}' ORDER BY updated_at DESC"
    return query_shadow_db(query)

@mcp.tool()
def get_session_messages(session_id: str):
    """
    Retrieve all messages within a specific chat session.
    """
    query = f"SELECT role, content, timestamp FROM messages WHERE session_id = '{session_id}' ORDER BY timestamp ASC"
    return query_shadow_db(query)

if __name__ == "__main__":
    mcp.run()
