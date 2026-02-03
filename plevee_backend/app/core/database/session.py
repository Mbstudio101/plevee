"""
Database session and models
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.config import settings

# Create database engine (optional - will be None if DATABASE_URL not set)
engine = None
SessionLocal = None

try:
    if settings.DATABASE_URL:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print("✅ Database engine created")
    else:
        print("⚠️  DATABASE_URL not set - running without database")
except Exception as e:
    print(f"⚠️  Could not connect to database: {e}")
    print("   Backend will run without database features")

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    if SessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Database not available. Please start PostgreSQL or configure DATABASE_URL in .env file."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
