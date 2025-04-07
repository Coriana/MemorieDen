# initialize_db.py
from database import engine, Base
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Enable foreign key constraints
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")

    # Create FTS5 virtual table for memories
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts 
                USING fts5(content, memory_id, tokenize='porter');
            """))
            logger.info("FTS5 virtual table 'memories_fts' created.")
        except Exception as e:
            logger.error(f"Failed to create FTS5 table: {e}")

if __name__ == "__main__":
    init_db()
