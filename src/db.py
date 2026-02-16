from pathlib import Path
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Float, Integer

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)  
    title = Column(String)
    company = Column(String)
    location = Column(String)
    category = Column(String, nullable=True)
    created = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_is_predicted = Column(Integer, nullable=True)
    salary_interval = Column(String, nullable=True) 
    currency = Column(String, nullable=True)

def get_engine(db_path: Path):
    return create_engine(f"sqlite:///{db_path}", future=True)

def init_db(engine):
    Base.metadata.create_all(engine)

def get_session(engine):
    return sessionmaker(bind=engine, future=True)()