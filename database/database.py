from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Import Base from models
from models.base import Base

# ----------------------------------------------------
# Load environment variables from .env file
# ----------------------------------------------------
load_dotenv()

# ----------------------------------------------------
# Get database URL from environment variable
# ----------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in environment variables")


# ----------------------------------------------------
# Create database engine
# ----------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)


# ----------------------------------------------------
# Create session factory
# ----------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ----------------------------------------------------
# Dependency used in FastAPI routes
# Provides DB session to endpoints
# ----------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()