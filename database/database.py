from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import Base from models
from models.base import Base

DATABASE_URL = "postgresql://postgres.zvahajdrcphsxynrhfzw:Praibha%402004@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

# Create database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Dependency used in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()