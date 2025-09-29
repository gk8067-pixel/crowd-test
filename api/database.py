import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 載入 .env（若有）
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app@localhost:5432/crowdtest")

# SQLAlchemy engine & Session
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 給 FastAPI 依賴注入用
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
