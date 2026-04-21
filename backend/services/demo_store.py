import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


_LOCK = threading.Lock()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _store_path() -> Path:
    return _project_root() / "data" / "demo_store.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_store() -> Dict[str, Any]:
    return {
        "students": {
            "STU001": {
                "student_id": "STU001",
                "name": "Ravi Kumar",
                "email": "ravi@example.com",
                "cgpa": 8.1,
                "created_at": _now_iso(),
            }
        },
        "scores": {
            "STU001": {
                "technical": 90.0,
                "cognitive": 85.0,
                "resume": 69.0,
                "video_ai": 1.0,
                "behavioral": 73.0,
                "updated_at": _now_iso(),
            }
        },
        "test_history": {
            "STU001": [
                {
                    "test_id": "technical",
                    "test_name": "Technical Skills Assessment",
                    "type": "technical",
                    "score": 90.0,
                    "status": "Passed",
                    "date": "2026-03-23",
                },
                {
                    "test_id": "cognitive",
                    "test_name": "Cognitive Ability Assessment",
                    "type": "cognitive",
                    "score": 80.0,
                    "status": "Passed",
                    "date": "2026-03-23",
                },
                {
                    "test_id": "communication",
                    "test_name": "Communication Skills Assessment",
                    "type": "communication",
                    "score": 90.0,
                    "status": "Passed",
                    "date": "2026-03-23",
                },
                {
                    "test_id": "psychometric",
                    "test_name": "Behavioural & Personality Assessment",
                    "type": "psychometric",
                    "score": 72.5,
                    "status": "Passed",
                    "date": "2026-03-23",
                },
            ]
        },
        "resume": {"STU001": {"resume_text": "", "analysis": None, "updated_at": _now_iso()}},
        "interview": {"STU001": {"last_result": None, "updated_at": _now_iso()}},
    }


def load_store() -> Dict[str, Any]:
    path = _store_path()
    with _LOCK:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            data = _default_store()
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return data
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = _default_store()
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return data


def save_store(data: Dict[str, Any]) -> None:
    path = _store_path()
    with _LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def get_student(student_id: str) -> Optional[Dict[str, Any]]:
    store = load_store()
    return store.get("students", {}).get(student_id)


def upsert_student(student: Dict[str, Any]) -> Dict[str, Any]:
    store = load_store()
    students = store.setdefault("students", {})
    students[student["student_id"]] = {**students.get(student["student_id"], {}), **student, "updated_at": _now_iso()}
    save_store(store)
    return students[student["student_id"]]


def get_scores(student_id: str) -> Dict[str, float]:
    store = load_store()
    scores = store.get("scores", {}).get(student_id)
    if not scores:
        return {"technical": 0.0, "cognitive": 0.0, "resume": 0.0, "video_ai": 0.0, "behavioral": 0.0}
    return {
        "technical": float(scores.get("technical", 0.0)),
        "cognitive": float(scores.get("cognitive", 0.0)),
        "resume": float(scores.get("resume", 0.0)),
        "video_ai": float(scores.get("video_ai", 0.0)),
        "behavioral": float(scores.get("behavioral", 0.0)),
    }


def set_component_score(student_id: str, component: str, score: float) -> Dict[str, float]:
    component = component.lower()
    store = load_store()
    scores = store.setdefault("scores", {}).setdefault(student_id, {})
    scores[component] = float(score)
    scores["updated_at"] = _now_iso()
    save_store(store)
    return get_scores(student_id)


def add_test_attempt(student_id: str, attempt: Dict[str, Any]) -> List[Dict[str, Any]]:
    store = load_store()
    history = store.setdefault("test_history", {}).setdefault(student_id, [])
    history.insert(
        0,
        {
            "test_id": attempt.get("test_id"),
            "test_name": attempt.get("test_name"),
            "type": attempt.get("type"),
            "score": float(attempt.get("score", 0.0)),
            "status": attempt.get("status", "Completed"),
            "date": attempt.get("date") or datetime.now().strftime("%Y-%m-%d"),
            "raw": attempt.get("raw"),
        },
    )
    store.setdefault("test_history", {})[student_id] = history[:25]
    save_store(store)
    return store["test_history"][student_id]


def set_resume_analysis(student_id: str, resume_text: str, analysis: Dict[str, Any]) -> None:
    store = load_store()
    store.setdefault("resume", {}).setdefault(student_id, {})
    store["resume"][student_id] = {"resume_text": resume_text, "analysis": analysis, "updated_at": _now_iso()}
    save_store(store)


def get_resume_analysis(student_id: str) -> Optional[Dict[str, Any]]:
    store = load_store()
    return store.get("resume", {}).get(student_id, {}).get("analysis")


def set_interview_result(student_id: str, result: Dict[str, Any]) -> None:
    store = load_store()
    store.setdefault("interview", {}).setdefault(student_id, {})
    store["interview"][student_id] = {"last_result": result, "updated_at": _now_iso()}
    save_store(store)


def get_interview_result(student_id: str) -> Optional[Dict[str, Any]]:
    store = load_store()
    return store.get("interview", {}).get(student_id, {}).get("last_result")
