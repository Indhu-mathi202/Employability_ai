from __future__ import annotations

from typing import Any, Dict, List, Optional


def generate_questions(resume_analysis: Optional[Dict[str, Any]] = None, count: int = 5) -> List[str]:
    skills = []
    role = None

    if resume_analysis:
        role_recs = resume_analysis.get("recommended_roles") or []
        if role_recs and isinstance(role_recs, list) and isinstance(role_recs[0], dict):
            role = role_recs[0].get("role")

        found = resume_analysis.get("skills_found") or {}
        if isinstance(found, dict):
            for cat_skills in found.values():
                if isinstance(cat_skills, list):
                    skills.extend([s for s in cat_skills if isinstance(s, str)])

    skills = list(dict.fromkeys(skills))[:5]
    role = role or "your target role"

    base = [
        "Tell me about yourself in 60 seconds.",
        "Walk me through one project you are most proud of. What was your role and impact?",
        f"Why do you want to work as a {role}?",
        "Tell me about a time you handled a conflict or disagreement in a team.",
        "What is one weakness you are actively improving, and how?",
    ]

    if skills:
        base.insert(2, f"Explain one concept from {skills[0]} that you used in your projects.")
    return base[:count]


def evaluate_interview(
    *,
    eye_contact_ratio: float = 0.0,
    duration_seconds: float = 0.0,
    answered_count: int = 0,
    total_questions: int = 0,
) -> Dict[str, Any]:
    eye_contact_ratio = max(0.0, min(1.0, float(eye_contact_ratio)))
    duration_seconds = max(0.0, float(duration_seconds))

    completion = (answered_count / total_questions) if total_questions else 0.0
    completion_score = max(0.0, min(1.0, completion)) * 25.0
    eye_score = eye_contact_ratio * 50.0

    # Demo pacing: ideal 2-6 minutes
    pacing = 1.0
    if duration_seconds < 120:
        pacing = duration_seconds / 120
    elif duration_seconds > 360:
        pacing = max(0.6, 360 / duration_seconds)
    pacing_score = max(0.0, min(1.0, pacing)) * 25.0

    total = eye_score + completion_score + pacing_score
    total = max(0.0, min(100.0, total))

    improvements: List[str] = []
    if eye_contact_ratio < 0.5:
        improvements.append("Maintain camera eye contact (look at lens)")
    if completion < 0.8:
        improvements.append("Answer all questions fully")
    if duration_seconds < 120:
        improvements.append("Add more detail (use STAR format)")
    if duration_seconds > 480:
        improvements.append("Be more concise (keep answers focused)")

    strengths: List[str] = []
    if eye_contact_ratio >= 0.65:
        strengths.append("Good eye contact")
    if completion >= 0.8:
        strengths.append("Completed the session")
    if 120 <= duration_seconds <= 360:
        strengths.append("Good pacing")

    return {
        "video_ai_score": round(total, 1),
        "eye_contact_ratio": round(eye_contact_ratio, 3),
        "duration_seconds": round(duration_seconds, 1),
        "strengths": strengths,
        "improvements": improvements,
    }

