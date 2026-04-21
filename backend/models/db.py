from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker


Base = declarative_base()


def _default_sqlite_url() -> str:
    project_root = Path(__file__).resolve().parents[2]
    db_path = project_root / "data" / "app.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"


def get_database_url() -> str:
    # Prefer env var; otherwise use SQLite for demo reliability.
    return os.getenv("DATABASE_URL") or _default_sqlite_url()


def get_engine():
    url = get_database_url()
    connect_args: Dict[str, Any] = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(url, echo=False, future=True, connect_args=connect_args)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine(), future=True)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    student_id = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), nullable=True, index=True)
    cgpa = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    scores = relationship("ScoreSnapshot", back_populates="student", uselist=False, cascade="all, delete-orphan")
    attempts = relationship("AssessmentAttempt", back_populates="student", cascade="all, delete-orphan")


class ScoreSnapshot(Base):
    __tablename__ = "score_snapshots"
    __table_args__ = (UniqueConstraint("student_id", name="uq_score_student"),)

    id = Column(Integer, primary_key=True)
    student_id = Column(String(32), ForeignKey("students.student_id"), nullable=False, index=True)
    technical = Column(Float, default=0.0, nullable=False)
    cognitive = Column(Float, default=0.0, nullable=False)
    resume = Column(Float, default=0.0, nullable=False)
    video_ai = Column(Float, default=0.0, nullable=False)
    behavioral = Column(Float, default=0.0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    student = relationship("Student", back_populates="scores")


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(Integer, primary_key=True)
    student_id = Column(String(32), ForeignKey("students.student_id"), nullable=False, index=True)
    test_id = Column(String(64), nullable=False)
    test_name = Column(String(200), nullable=True)
    type = Column(String(64), nullable=True)
    score = Column(Float, default=0.0, nullable=False)
    status = Column(String(64), default="Completed", nullable=False)
    date = Column(String(32), nullable=True)
    raw = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    student = relationship("Student", back_populates="attempts")


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
