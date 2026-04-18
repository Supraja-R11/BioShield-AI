from sqlmodel import create_engine, SQLModel, Session
import os

DATABASE_URL = "sqlite:///./bioshield.db"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
