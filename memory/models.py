from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Enum, DateTime
import enum
from datetime import datetime
from memory.database import Base

class TaskState(enum.Enum):
    RUNNING = "RUNNING"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    COMPLETED = "COMPLETED"

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)
    permissions = Column(JSON)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Integer, default=1)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"))
    description = Column(Text)
    state = Column(Enum(TaskState), default=TaskState.RUNNING)
    created_at = Column(DateTime, default=datetime.utcnow)
    result = Column(Text, nullable=True)
    pending_approval_request = Column(Text, nullable=True)

class MemoryStore(Base):
    __tablename__ = "memory_store"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
