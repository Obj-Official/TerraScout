from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database file path
SQLITE_DATABASE_URL = "sqlite:///./terrascout.db"

# Create the SQLAlchemy engine for SQLite
engine = create_engine(
    SQLITE_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Needed for SQLite in FastAPI
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative class definitions
Base = declarative_base()

# Dependency to get the database session (used in FastAPI routes)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()