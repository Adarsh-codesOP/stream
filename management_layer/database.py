import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Adarsh%40123@localhost:5432/StreamLink"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Adarsh%40123@localhost:5433/StreamLink"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
