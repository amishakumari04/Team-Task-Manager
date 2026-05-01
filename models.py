import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default='Member') # Admin or Member

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    tasks = relationship("Task", back_populates="project", cascade="all, delete")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    status = Column(String, default='Todo') # Todo, Doing, Done
    due_date = Column(DateTime, default=datetime.now() + timedelta(days=3))
    project_id = Column(Integer, ForeignKey('projects.id'))
    assigned_to = Column(Integer, ForeignKey('users.id'))
    
    project = relationship("Project", back_populates="tasks")
    user = relationship("User")

# Database Setup: Uses Railway Environment variable or local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)