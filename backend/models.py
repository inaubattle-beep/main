from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, index=True)
    role = Column(String)
    permissions = Column(String)  # JSON string

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.id"))
    status = Column(String)  # RUNNING, WAITING_FOR_USER, COMPLETED
    data = Column(String)  # JSON string