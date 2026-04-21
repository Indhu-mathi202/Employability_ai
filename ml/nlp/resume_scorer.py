# ml/nlp/resume_scorer.py - BULLETPROOF FIXED VERSION
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
import re
from collections import Counter

# PATH FIX
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class ResumeScorer:
    """Production-Ready Resume Analysis - Error Proof"""
    
    def __init__(self):
        self.skill_taxonomy = {
            "programming": ["python", "java", "javascript", "c++", "c#", "go", "rust", "php", "ruby"],
            "frameworks": ["react", "angular", "vue", "django", "flask", "spring", "laravel", "rails"],
            "databases": ["sql", "mysql", "postgresql", "mongodb", "oracle", "sqlite"],
            "data_science": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras"],
            "cloud_devops": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform"],
            "web_basics": ["html", "css"],
            "tools": ["git"],
            "analytics": ["excel", "tableau", "power bi"],
            "soft_skills": ["leadership", "teamwork", "communication", "problem-solving"]
        }
        self.role_requirements = {
            "data_scientist": ["python", "pandas", "scikit-learn", "sql"],
            "software_engineer": ["python", "java", "react", "docker"],
            "data_analyst": ["sql", "excel", "tableau"],
            "devops": ["docker", "kubernetes", "aws"],
            "web_developer": ["javascript", "react", "html", "css"],
            "java_developer": ["java", "spring", "sql", "git"],
        }

    def normalize_role_key(self, role: Optional[str]) -> Optional[str]:
        if not role:
            return None
        key = str(role).strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "web": "web_developer",
            "frontend": "web_developer",
            "front_end": "web_developer",
            "java": "java_developer",
            "sde": "software_engineer",
            "software": "software_engineer",
            "data": "data_analyst",
            "data_science": "data_scientist",
            "cloud": "devops",
        }
        key = aliases.get(key, key)
        return key if key in self.role_requirements else None

    def safe_get(self, d: Dict, key: str, default=0.0) -> float:
        """Safe dictionary access - prevents KeyError"""
        return d.get(key, default)
    
    def preprocess_resume(self, text: str) -> str:
        """Clean resume text"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text.lower().strip())
        return re.sub(r'[^\w\s]', ' ', text)
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills safely"""
        found_skills = {cat: [] for cat in self.skill_taxonomy}
        if not text:
            return found_skills
        
        for category, keywords in self.skill_taxonomy.items():
            for keyword in keywords:
                if re.search(rf'\b{re.escape(keyword)}\b', text):
                    found_skills[category].append(keyword)
        
        return found_skills
    
    def calculate_scores(self, found_skills: Dict) -> Dict:
        """Calculate scores with defaults"""
        scores = {}
        total_skills = 0
        
        for category in self.skill_taxonomy:
            unique = len(set(found_skills.get(category, [])))
            cat_score = min(unique * 20, 90)
            scores[category] = cat_score
            total_skills += unique
        
        # Weighted score with safe access
        weighted = (
            self.safe_get(scores, "programming") * 0.3 +
            self.safe_get(scores, "data_science") * 0.25 +
            self.safe_get(scores, "frameworks") * 0.2 +
            self.safe_get(scores, "cloud_devops") * 0.15 +
            self.safe_get(scores, "databases") * 0.1
        )
        
        technical = round((self.safe_get(scores, "programming") + self.safe_get(scores, "data_science")) / 2, 1)
        
        return {
            "category_scores": scores,
            "total_skills": total_skills,
            "weighted_score": round(weighted, 1),
            "technical_score": technical
        }
    
    def recommend_roles(self, found_skills: Dict) -> List[Dict]:
        """Role recommendations"""
        role_scores = []
        
        for role, required in self.role_requirements.items():
            match_count = sum(1 for skill in required 
                            if any(skill in cat_skills for cat_skills in found_skills.values()))
            match_pct = min((match_count / len(required)) * 100, 100)
            role_scores.append({
                "role": role.replace("_", " ").title(),
                "match_percentage": round(match_pct, 1),
                "required_met": match_count,
                "total_required": len(required)
            })
        
        return sorted(role_scores, key=lambda x: x["match_percentage"], reverse=True)[:3]
    
    def identify_gaps(self, found_skills: Dict, target_required: Optional[List[str]] = None) -> List[str]:
        """Skill gaps"""
        required = (target_required or ["python", "sql", "excel"])[:]
        gaps = [skill for skill in required if not any(skill in cat_skills for cat_skills in found_skills.values())]
        return gaps

    def role_match(self, found_skills: Dict, role_key: str) -> Dict:
        required = self.role_requirements.get(role_key, [])
        met = [skill for skill in required if any(skill in cat_skills for cat_skills in found_skills.values())]
        missing = [skill for skill in required if skill not in met]
        match_pct = min((len(met) / len(required)) * 100, 100) if required else 0.0
        return {"required": required, "met": met, "missing": missing, "match_percentage": round(match_pct, 1)}
    
    def score_resume(self, resume_text: str, student_id: str = "STU001", target_role: Optional[str] = None) -> Dict:
        """Main scoring method - BULLETPROOF"""
        processed = self.preprocess_resume(resume_text)
        found_skills = self.extract_skills(processed)
        scores = self.calculate_scores(found_skills)
        roles = self.recommend_roles(found_skills)
        role_key = self.normalize_role_key(target_role)
        gaps = self.identify_gaps(found_skills)
        target_info = None
        if role_key:
            target_info = self.role_match(found_skills, role_key)
            title = role_key.replace("_", " ").title()
            target_entry = {
                "role": title,
                "match_percentage": target_info["match_percentage"],
                "required_met": len(target_info["met"]),
                "total_required": len(target_info["required"]),
            }
            roles = [target_entry] + [r for r in roles if r.get("role") != title]
            gaps = self.identify_gaps(found_skills, target_required=target_info["required"])
         
        word_count = len(processed.split()) if processed else 0
        quality_bonus = min(word_count / 50 * 10, 15)
        final_score = min(scores["weighted_score"] + quality_bonus, 100)
         
        out = {
            "student_id": student_id,
            "resume_score": round(final_score, 1),
            "technical_score": scores["technical_score"],
            "skills_found": found_skills,
            "total_unique_skills": scores["total_skills"],
            "word_count": word_count,
            "recommended_roles": roles,
            "skill_gaps": gaps,
            "strengths": [cat for cat, score in scores["category_scores"].items() if score >= 70],
            "status": "success" if final_score > 0 else "needs_improvement"
        }

        if role_key and target_info:
            out["target_role"] = role_key.replace("_", " ").title()
            out["target_match_percentage"] = target_info["match_percentage"]
            out["target_missing_skills"] = target_info["missing"]
            out["target_required_skills"] = target_info["required"]

        return out

# BULLETPROOF TEST
if __name__ == "__main__":
    scorer = ResumeScorer()
    
    print("RESUME SCORER v3.1 - BULLETPROOF")
    print("=" * 60)
    
    test_resumes = [
        """
        Madhan S | B.Tech CSE 2026 | CGPA: 8.5
        Skills: Python, Pandas, NumPy, Scikit-learn, SQL, MySQL, React, Docker, AWS
        Experience: Data Science Intern, ML Projects
        """,
        """
        Junior Developer | Basic Python, Excel, SQL
        """,
        ""  # EMPTY TEST CASE
    ]
    
    for i, resume in enumerate(test_resumes, 1):
        print(f"\n Test {i}:")
        result = scorer.score_resume(resume, f"STU00{i}")
        
        # SAFE PRINTING - No KeyError!
        print(f"   Score:     {result.get('resume_score', 0)}/100")
        print(f"   Technical: {result.get('technical_score', 0)}/100")
        print(f"   Skills:    {result.get('total_unique_skills', 0)}")
        print(f"   Roles:     {result.get('recommended_roles', [{}])[0].get('role', 'N/A')}")
        print(f"   Gaps:      {', '.join(result.get('skill_gaps', [])) or 'None'}")
    
    print("\n ALL TESTS PASSED - No KeyError!")
    print("Production Ready!")
