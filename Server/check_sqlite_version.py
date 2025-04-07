# Before:
import sqlite3

# After:
import pysqlite3 as sqlite3

print(sqlite3.sqlite_version)

def check_fts5_and_bm25():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    try:
        cursor.execute("CREATE VIRTUAL TABLE test_fts USING fts5(content)")
        print("FTS5 is supported.")
    except sqlite3.OperationalError as e:
        print(f"FTS5 is not supported: {e}")
        conn.close()
        return
    
    try:
        # Insert sample data
        cursor.execute("INSERT INTO test_fts (content) VALUES ('Science is fascinating')")
        cursor.execute("SELECT bm25() FROM test_fts")
        rank = cursor.fetchone()[0]
        print(f"bm25() is supported. Example rank: {rank}")
    except sqlite3.OperationalError as e:
        print(f"bm25() is not supported: {e}")
    
    cursor.close()
    conn.close()

check_fts5_and_bm25()
