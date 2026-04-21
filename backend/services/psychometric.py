# backend/services/psychometric.py - FIXED VERSION
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))  # Add project root to path

from typing import Dict, List, Optional
from datetime import datetime
import random

# Try importing schemas, fallback if not available
try:
    from data.schemas import PsychometricResult
except ImportError:
    # Fallback schema definition
    from pydantic import BaseModel
    from typing import Dict, List, Optional
    
    class PsychometricResult(BaseModel):
        student_id: str
        extraversion: float
        agreeableness: float
        conscientiousness: float
        neuroticism: float
        openness: float
        behavioral_score: float
        evaluated_at: Optional[datetime] = datetime.now()

# Complete Big-5 Questionnaire (10 items per trait)
BIG5_QUESTIONS = [
    # Extraversion (10 items)
    {"id": 1,  "text": "I am talkative", "trait": "extraversion", "reverse": False},
    {"id": 6,  "text": "I am reserved", "trait": "extraversion", "reverse": True},
    {"id": 11, "text": "I feel comfortable around people", "trait": "extraversion", "reverse": False},
    {"id": 16, "text": "I keep in the background", "trait": "extraversion", "reverse": True},
    {"id": 21, "text": "I start conversations", "trait": "extraversion", "reverse": False},
    {"id": 26, "text": "I have little to say", "trait": "extraversion", "reverse": True},
    {"id": 31, "text": "I talk to a lot of different people", "trait": "extraversion", "reverse": False},
    {"id": 36, "text": "I don't talk a lot", "trait": "extraversion", "reverse": True},
    {"id": 41, "text": "I don't mind being the center of attention", "trait": "extraversion", "reverse": False},
    {"id": 46, "text": "I am quiet around strangers", "trait": "extraversion", "reverse": True},
    
    # Agreeableness (10 items)
    {"id": 2,  "text": "I sympathize with others' feelings", "trait": "agreeableness", "reverse": False},
    {"id": 7,  "text": "I get upset easily", "trait": "agreeableness", "reverse": True},
    {"id": 12, "text": "I feel others' emotions", "trait": "agreeableness", "reverse": False},
    {"id": 17, "text": "I insult people", "trait": "agreeableness", "reverse": True},
    {"id": 22, "text": "I am not interested in other people's problems", "trait": "agreeableness", "reverse": True},
    {"id": 27, "text": "I am not really interested in others", "trait": "agreeableness", "reverse": True},
    {"id": 32, "text": "I take time out for others", "trait": "agreeableness", "reverse": False},
    {"id": 37, "text": "I feel little concern for others", "trait": "agreeableness", "reverse": True},
    {"id": 42, "text": "I make people feel at ease", "trait": "agreeableness", "reverse": False},
    {"id": 47, "text": "I am sometimes rude to others", "trait": "agreeableness", "reverse": True},
    
    # Conscientiousness (10 items)
    {"id": 3,  "text": "I am always prepared", "trait": "conscientiousness", "reverse": False},
    {"id": 8,  "text": "I leave my belongings around", "trait": "conscientiousness", "reverse": True},
    {"id": 13, "text": "I pay attention to details", "trait": "conscientiousness", "reverse": False},
    {"id": 18, "text": "I make a mess of things", "trait": "conscientiousness", "reverse": True},
    {"id": 23, "text": "I get chores done right away", "trait": "conscientiousness", "reverse": False},
    {"id": 28, "text": "I often forget to put things back", "trait": "conscientiousness", "reverse": True},
    {"id": 33, "text": "I like order", "trait": "conscientiousness", "reverse": False},
    {"id": 38, "text": "I shirk my duties", "trait": "conscientiousness", "reverse": True},
    {"id": 43, "text": "I follow a schedule", "trait": "conscientiousness", "reverse": False},
    {"id": 48, "text": "I find it difficult to get down to work", "trait": "conscientiousness", "reverse": True},
    
    # Neuroticism (10 items)
    {"id": 4,  "text": "I get stressed out easily", "trait": "neuroticism", "reverse": False},
    {"id": 9,  "text": "I am relaxed most of the time", "trait": "neuroticism", "reverse": True},
    {"id": 14, "text": "I worry about things", "trait": "neuroticism", "reverse": False},
    {"id": 19, "text": "I seldom feel blue", "trait": "neuroticism", "reverse": True},
    {"id": 24, "text": "I am easily disturbed", "trait": "neuroticism", "reverse": False},
    {"id": 29, "text": "I have frequent mood swings", "trait": "neuroticism", "reverse": False},
    {"id": 34, "text": "I get irritated easily", "trait": "neuroticism", "reverse": False},
    {"id": 39, "text": "I keep my emotions under control", "trait": "neuroticism", "reverse": True},
    {"id": 44, "text": "I panic easily under pressure", "trait": "neuroticism", "reverse": False},
    {"id": 49, "text": "I suffer from nervous feelings", "trait": "neuroticism", "reverse": False},
    
    # Openness (10 items)
    {"id": 5,  "text": "I have a rich vocabulary", "trait": "openness", "reverse": False},
    {"id": 10, "text": "I have difficulty understanding abstract ideas", "trait": "openness", "reverse": True},
    {"id": 15, "text": "I have a vivid imagination", "trait": "openness", "reverse": False},
    {"id": 20, "text": "I am not interested in abstract ideas", "trait": "openness", "reverse": True},
    {"id": 25, "text": "I have excellent ideas", "trait": "openness", "reverse": False},
    {"id": 30, "text": "I do not have a good imagination", "trait": "openness", "reverse": True},
    {"id": 35, "text": "I am quick to understand things", "trait": "openness", "reverse": False},
    {"id": 40, "text": "I use difficult words", "trait": "openness", "reverse": False},
    {"id": 45, "text": "I spend time reflecting on things", "trait": "openness", "reverse": False},
    {"id": 50, "text": "I am full of ideas", "trait": "openness", "reverse": False},
]

class PsychometricEngine:
    """Complete Big-5 Psychometric Assessment (50 items)"""
    
    def __init__(self):
        self.traits = ["extraversion", "agreeableness", "conscientiousness", "neuroticism", "openness"]
    
    def get_questions(self, num_questions: Optional[int] = None) -> List[Dict]:
        """Get Big-5 questions (full 50 or subset)"""
        questions = [{"id": q["id"], "text": q["text"]} for q in BIG5_QUESTIONS]
        if num_questions:
            questions = random.sample(questions, min(num_questions, len(questions)))
        return questions
    
    def score_responses(self, responses: Dict[int, int], student_id: str = "STU001") -> PsychometricResult:
        """Score Big-5 responses (1-5 Likert scale)"""
        trait_scores = {trait: [] for trait in self.traits}
        
        # Score each question
        for q in BIG5_QUESTIONS:
            qid = q["id"]
            if qid in responses:
                score = responses[qid]
                # Reverse score for reverse-coded items
                if q["reverse"]:
                    score = 6 - score
                trait_scores[q["trait"]].append(score)
        
        # Calculate trait averages (0-100 scale)
        result = {}
        for trait, scores in trait_scores.items():
            if scores:
                avg = sum(scores) / len(scores)
                result[trait] = round(((avg - 1) / 4) * 100, 2)
            else:
                result[trait] = 0.0
        
        # Calculate behavioral score for employability
        behavioral_score = (
            result.get("conscientiousness", 0) * 0.40 +
            result.get("agreeableness", 0) * 0.25 +
            result.get("extraversion", 0) * 0.20 +
            result.get("openness", 0) * 0.15
        )
        result["behavioral_score"] = round(behavioral_score, 2)
        
        return PsychometricResult(
            student_id=student_id,
            extraversion=result["extraversion"],
            agreeableness=result["agreeableness"],
            conscientiousness=result["conscientiousness"],
            neuroticism=result["neuroticism"],
            openness=result["openness"],
            behavioral_score=result["behavioral_score"]
        )
    
    def get_job_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate job role recommendations"""
        recommendations = []
        if scores.get("extraversion", 0) > 70:
            recommendations.extend(["Sales", "Marketing", "Customer Success"])
        if scores.get("conscientiousness", 0) > 75:
            recommendations.extend(["Project Management", "Accounting"])
        if scores.get("agreeableness", 0) > 70:
            recommendations.extend(["HR", "Customer Support"])
        if scores.get("openness", 0) > 70:
            recommendations.extend(["Research", "Design"])
        return recommendations[:3] if recommendations else ["General Roles"]

if __name__ == "__main__":
    engine = PsychometricEngine()
    
    print("PSYCHOMETRIC ENGINE v2.0 - Big-5 Complete")
    print("=" * 60)
    
    # Test scoring
    sample_responses = {
        1: 4, 6: 2, 11: 5, 16: 1, 21: 4,  # High Extraversion sample
        2: 5, 7: 1, 12: 4, 17: 1, 32: 5,  # High Agreeableness sample
        3: 5, 8: 1, 13: 5, 18: 1, 23: 5,  # High Conscientiousness sample
        4: 2, 9: 4, 14: 2, 19: 4, 24: 2,  # Low Neuroticism sample
        5: 4, 10: 2, 15: 4, 20: 2, 25: 5   # High Openness sample
    }
    
    result = engine.score_responses(sample_responses, "STU001")
    
    print("\n Big-5 Results:")
    print(f"   Extraversion:     {result.extraversion:.1f}%")
    print(f"   Agreeableness:    {result.agreeableness:.1f}%")
    print(f"   Conscientiousness:{result.conscientiousness:.1f}%")
    print(f"   Neuroticism:      {result.neuroticism:.1f}%")
    print(f"   Openness:         {result.openness:.1f}%")
    print(f"   Behavioral Score: {result.behavioral_score:.1f}%")
    
    print("\n FIXED - Now runs from anywhere!")
