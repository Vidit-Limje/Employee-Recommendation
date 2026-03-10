from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres.zvahajdrcphsxynrhfzw:Praibha%402004@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)