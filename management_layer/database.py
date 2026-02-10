import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Update this url
# this one to postgresql://user:password@host:port/database_name
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Adarsh%40123@localhost:5432/StreamLink")

# For Local Execution with Dockerized DB (Port 5433)
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5433/StreamLink"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
