from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"  # Example database URL; replace with actual one.

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only for SQLite; remove for other DBs.
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush = False,
    bind = engine
)





