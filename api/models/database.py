"""
Database connection and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment variable or use default SQLite for development
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/chaoschain"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()


# Dependency to get a database session
def get_db():
    """
    Creates a database session and handles its lifecycle.
    
    Yields:
        SQLAlchemy session: A database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 