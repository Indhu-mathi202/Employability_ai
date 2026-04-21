from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from backend.models.db import (
    AssessmentAttempt,
    ScoreSnapshot,
    Student,
    init_db,
    session_scope,
)
from backend.services import demo_store


def _db_ready() -> bool:
    try:
        init_db()
        return True
    except Exception:
        return False


def _ensure_scores(session, student_id: str) -> ScoreSnapshot:
    scores = session.query(ScoreSnapshot).filter(ScoreSnapshot.student_id == student_id).one_or_none()
    if scores:
        return scores
    scores = ScoreSnapshot(student_id=student_id)
    session.add(scores)
    session.flush()
    return scores


def upsert_student(student: Dict[str, Any]) -> Dict[str, Any]:
    if not _db_ready():
        return demo_store.upsert_student(student)

    sid = student["student_id"]
    with session_scope() as session:
        existing = session.query(Student).filter(Student.student_id == sid).one_or_none()
        now = datetime.utcnow()
        if existing:
            existing.name = student.get("name") or existing.name
            existing.email = student.get("email") or existing.email
            existing.cgpa = student.get("cgpa", existing.cgpa)
            existing.updated_at = now
            _ensure_scores(session, sid)
            session.flush()
            return {
                "student_id": existing.student_id,
                "name": existing.name,
                "email": existing.email,
                "cgpa": existing.cgpa,
            }

        created = Student(
            student_id=sid,
            name=student.get("name") or sid,
            email=student.get("email"),
            cgpa=student.get("cgpa"),
            created_at=now,
            updated_at=now,
        )
        session.add(created)
        session.flush()
        _ensure_scores(session, sid)
        return {"student_id": created.student_id, "name": created.name, "email": created.email, "cgpa": created.cgpa}


def get_student(student_id: str) -> Optional[Dict[str, Any]]:
    if not _db_ready():
        return demo_store.get_student(student_id)
    with session_scope() as session:
        s = session.query(Student).filter(Student.student_id == student_id).one_or_none()
        if not s:
            return None
        return {"student_id": s.student_id, "name": s.name, "email": s.email, "cgpa": s.cgpa}


def get_scores(student_id: str) -> Dict[str, float]:
    if not _db_ready():
        return demo_store.get_scores(student_id)
    with session_scope() as session:
        scores = session.query(ScoreSnapshot).filter(ScoreSnapshot.student_id == student_id).one_or_none()
        if not scores:
            return {"technical": 0.0, "cognitive": 0.0, "resume": 0.0, "video_ai": 0.0, "behavioral": 0.0}
        return {
            "technical": float(scores.technical),
            "cognitive": float(scores.cognitive),
            "resume": float(scores.resume),
            "video_ai": float(scores.video_ai),
            "behavioral": float(scores.behavioral),
        }


def set_component_score(student_id: str, component: str, score: float) -> Dict[str, float]:
    component = component.lower()
    if not _db_ready():
        return demo_store.set_component_score(student_id, component, score)

    with session_scope() as session:
        _ensure_scores(session, student_id)
        scores = session.query(ScoreSnapshot).filter(ScoreSnapshot.student_id == student_id).one()
        if hasattr(scores, component):
            setattr(scores, component, float(score))
        scores.updated_at = datetime.utcnow()
        session.flush()
    return get_scores(student_id)


def add_test_attempt(student_id: str, attempt: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not _db_ready():
        return demo_store.add_test_attempt(student_id, attempt)
    with session_scope() as session:
        a = AssessmentAttempt(
            student_id=student_id,
            test_id=attempt.get("test_id") or "",
            test_name=attempt.get("test_name"),
            type=attempt.get("type"),
            score=float(attempt.get("score", 0.0)),
            status=attempt.get("status") or "Completed",
            date=attempt.get("date") or datetime.now().strftime("%Y-%m-%d"),
            raw=attempt.get("raw"),
        )
        session.add(a)
        session.flush()
    return get_test_history(student_id)


def get_test_history(student_id: str) -> List[Dict[str, Any]]:
    if not _db_ready():
        store = demo_store.load_store()
        return store.get("test_history", {}).get(student_id, [])
    with session_scope() as session:
        rows = (
            session.query(AssessmentAttempt)
            .filter(AssessmentAttempt.student_id == student_id)
            .order_by(AssessmentAttempt.id.desc())
            .limit(25)
            .all()
        )
        return [
            {
                "test_id": r.test_id,
                "test_name": r.test_name,
                "type": r.type,
                "score": float(r.score),
                "status": r.status,
                "date": r.date,
                "raw": r.raw,
            }
            for r in rows
        ]
