from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


WEIGHTS = {
    "technical": 0.30,
    "cognitive": 0.20,
    "resume": 0.20,
    "video_ai": 0.15,
    "behavioral": 0.15,
}


def _clamp_0_100(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def compute_overall(scores: Dict[str, float]) -> float:
    total = 0.0
    for k, w in WEIGHTS.items():
        total += _clamp_0_100(scores.get(k, 0.0)) * w
    return round(_clamp_0_100(total), 1)


def compute_placement_probability(overall: float, cgpa: Optional[float] = None) -> float:
    overall = _clamp_0_100(overall)
    cgpa_val = float(cgpa) if cgpa is not None else 7.5
    # Demo formula: employability drives probability, CGPA nudges it a bit
    prob = overall * 0.78 + (cgpa_val - 6.0) * 6.0 - 5.0
    return round(_clamp_0_100(prob), 1)


def default_roles(scores: Dict[str, float]) -> List[str]:
    technical = scores.get("technical", 0.0)
    cognitive = scores.get("cognitive", 0.0)
    roles: List[str] = []
    if technical >= 75:
        roles.extend(["ML Engineer", "Data Scientist", "Software Engineer"])
    elif technical >= 60:
        roles.extend(["Data Analyst", "Full Stack Developer"])
    if cognitive >= 70:
        roles.append("DevOps Engineer")
    return (roles or ["Entry Level Engineer"])[:3]


def default_skill_gaps(scores: Dict[str, float]) -> List[str]:
    gaps = []
    if scores.get("technical", 0.0) < 65:
        gaps.append("DSA")
    if scores.get("resume", 0.0) < 65:
        gaps.append("Projects")
    if scores.get("cognitive", 0.0) < 60:
        gaps.append("Aptitude")
    if scores.get("behavioral", 0.0) < 60:
        gaps.append("Teamwork")
    if scores.get("video_ai", 0.0) < 60:
        gaps.append("Eye Contact")
    return gaps[:6]


@dataclass
class Scorecard:
    student_id: str
    employability_score: float
    placement_probability: float
    score_breakdown: Dict[str, float]
    top_roles: List[str]
    skill_gaps: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "employability_score": self.employability_score,
            "placement_probability": self.placement_probability,
            "top_roles": self.top_roles,
            "skill_gaps": self.skill_gaps,
            "weights": {k: int(v * 100) for k, v in WEIGHTS.items()},
            "score_breakdown": self.score_breakdown,
        }


def build_scorecard(
    student_id: str,
    scores: Dict[str, float],
    cgpa: Optional[float] = None,
    resume_analysis: Optional[Dict[str, Any]] = None,
) -> Scorecard:
    overall = compute_overall(scores)
    placement_prob = compute_placement_probability(overall, cgpa=cgpa)

    roles = None
    gaps = None
    if resume_analysis:
        roles = [r.get("role") for r in resume_analysis.get("recommended_roles", []) if isinstance(r, dict) and r.get("role")]
        gaps = [g for g in resume_analysis.get("skill_gaps", []) if isinstance(g, str)]

    top_roles = (roles or default_roles(scores))[:3]
    skill_gaps = (gaps or default_skill_gaps(scores))[:8]

    return Scorecard(
        student_id=student_id,
        employability_score=overall,
        placement_probability=placement_prob,
        score_breakdown={
            "technical": float(scores.get("technical", 0.0)),
            "cognitive": float(scores.get("cognitive", 0.0)),
            "resume": float(scores.get("resume", 0.0)),
            "video_ai": float(scores.get("video_ai", 0.0)),
            "behavioral": float(scores.get("behavioral", 0.0)),
        },
        top_roles=top_roles,
        skill_gaps=skill_gaps,
    )

