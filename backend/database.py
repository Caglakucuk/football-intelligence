import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL .env dosyasinda bulunamadi")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

@event.listens_for(engine, "begin")
def set_search_path(conn):
    conn.exec_driver_sql("SET LOCAL search_path TO public")

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)