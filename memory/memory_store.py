"""In-memory storage for AI OS core components.
Optionally backed by PostgreSQL if DATABASE_URL is provided.
"""
from typing import Dict, List, Any
import os
import datetime

# Optional DB support via SQLAlchemy Core (no ORM dependency required here)
try:
    from sqlalchemy import create_engine, MetaData, Table, Column, String, Text, DateTime, Integer
    from sqlalchemy.exc import SQLAlchemyError
    _SQLALCHEMY_AVAILABLE = True
except Exception:
    _SQLALCHEMY_AVAILABLE = False


class MemoryStore:
    def __init__(self):
        self.use_db = False
        self.engine = None
        self.metadata = None
        self.tasks_table = None
        self.logs_table = None
        self.decisions_table = None
        self._init_storage()
        self._logs_buffer: List[str] = []

    def _init_storage(self):
        db_url = os.environ.get("DATABASE_URL")
        if _SQLALCHEMY_AVAILABLE and db_url:
            try:
                self.engine = create_engine(db_url, future=True)
                self.metadata = MetaData()
                self.tasks_table = Table(
                    'tasks', self.metadata,
                    Column('id', String, primary_key=True),
                    Column('description', Text),
                    Column('status', String(50)),
                    Column('agent_id', String(100)),
                    Column('result', Text),
                )
                self.logs_table = Table(
                    'logs', self.metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('message', Text),
                    Column('ts', DateTime, default=datetime.datetime.utcnow),
                )
                self.decisions_table = Table(
                    'decisions', self.metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('task_id', String(100)),
                    Column('plan', Text),
                )
                self.metadata.create_all(self.engine)
                self.use_db = True
            except SQLAlchemyError:
                self.use_db = False
        # Fallback to in-memory if no DB configured or failed to initialize
        if not self.use_db:
            self.tasks: Dict[str, Dict[str, Any]] = {}
            self.logs: List[str] = []
            self.decisions: List[Dict[str, Any]] = []

    # Task management
    def add_task(self, task_id: str, payload: Dict[str, Any]):
        if self.use_db:
            with self.engine.connect() as conn:
                ins = self.tasks_table.insert().values(
                    id=task_id,
                    description=payload.get("description"),
                    status=payload.get("status", "PENDING"),
                    agent_id=payload.get("agent_id"),
                    result=None,
                )
                conn.execute(ins)
                conn.commit()
        else:
            self.tasks[task_id] = payload
            self._log(f"Task added: {task_id}")

    def complete_task(self, task_id: str, result: Any = None):
        if self.use_db:
            with self.engine.connect() as conn:
                upd = self.tasks_table.update().where(self.tasks_table.c.id == task_id).values(status="COMPLETED", result=result)
                conn.execute(upd)
                conn.commit()
        else:
            if task_id in getattr(self, 'tasks', {}):
                self.tasks[task_id]["status"] = "COMPLETED"
                self.tasks[task_id]["result"] = result
            self._log(f"Task completed: {task_id}")

    def add_log(self, log: str):
        self._log(log)

    def _log(self, msg: str):
        if self.use_db:
            with self.engine.connect() as conn:
                ins = self.logs_table.insert().values(message=msg, ts=datetime.datetime.utcnow())
                conn.execute(ins)
                conn.commit()
        else:
            self.logs.append(msg)

    def get_logs(self) -> List[str]:
        if self.use_db:
            with self.engine.connect() as conn:
                sel = self.logs_table.select()
                res = conn.execute(sel).fetchall()
                return [r[1] for r in res]
        return self.logs
