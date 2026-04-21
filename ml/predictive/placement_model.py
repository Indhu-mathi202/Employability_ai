# ml/predictive/placement_model.py - ENHANCED ML VERSION (Phase 5 Complete)
import sys
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, r2_score
import joblib
import random

# Fix import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class PlacementPredictor:
    """Advanced ML-powered Placement Prediction System (Phase 5)"""
    
    def __init__(self):
        self.placement_model = None
        self.salary_model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.salary_ranges = {
            "Freshers": (3, 6),
            "Junior": (6, 12),
            "Mid": (12, 25),
            "Senior": (25, 50)
        }
    
    def generate_synthetic_dataset(self, n_samples: int = 1000) -> pd.DataFrame:
        """Generate realistic synthetic dataset for ML training"""
        data = []
        
        for i in range(n_samples):
            cgpa = round(random.uniform(4.0, 10.0), 1)
            technical_score = round(random.uniform(20, 100), 1)
            communication_score = round(random.uniform(20, 100), 1)
            behavioral_score = round(random.uniform(20, 100), 1)
            cognitive_score = round(random.uniform(20, 100), 1)
            resume_score = round(random.uniform(20, 100), 1)
            
            # Overall employability score
            overall = (technical_score * 0.35 + 
                      communication_score * 0.20 + 
                      behavioral_score * 0.20 + 
                      cognitive_score * 0.15 + 
                      resume_score * 0.10)
            
            # Placement probability logic
            base_prob = overall / 100
            cgpa_boost = min((cgpa - 6.0) / 4.0, 0.3)
            prob = min(base_prob + cgpa_boost + random.uniform(-0.1, 0.1), 1.0)
            
            is_placed = 1 if random.random() < prob else 0
            
            # Salary prediction (only for placed students)
            if is_placed:
                salary = self.predict_salary(cgpa, technical_score, overall)
            else:
                salary = 0
        
            data.append({
                'student_id': f'STU{i:04d}',
                'cgpa': cgpa,
                'technical_score': technical_score,
                'communication_score': communication_score,
                'behavioral_score': behavioral_score,
                'cognitive_score': cognitive_score,
                'resume_score': resume_score,
                'overall_score': round(overall, 1),
                'is_placed': is_placed,
                'salary': salary
            })
        
        return pd.DataFrame(data)
    
    def predict_salary(self, cgpa: float, technical_score: float, overall: float) -> float:
        """Predict salary based on multiple factors"""
        base_salary = 4.0  # LPA for freshers
        cgpa_factor = min((cgpa - 6.0) / 4.0 * 2, 3.0)
        technical_factor = min(technical_score / 100 * 8, 8.0)
        overall_factor = min(overall / 100 * 5, 5.0)
        
        salary = base_salary + cgpa_factor + technical_factor + overall_factor
        return round(random.uniform(salary * 0.8, salary * 1.2), 1)
    
    def train_models(self, train_data: pd.DataFrame):
        """Train GradientBoosting (placement) + RandomForest (salary) models"""
        # Prepare features
        feature_cols = ['cgpa', 'technical_score', 'communication_score', 
                       'behavioral_score', 'cognitive_score', 'resume_score']
        X = train_data[feature_cols]
        y_placement = train_data['is_placed']
        y_salary = train_data[train_data['is_placed'] == 1]['salary'].fillna(0)
        
        # Split data
        X_train, X_test, y_train_p, y_test_p = train_test_split(
            X, y_placement, test_size=0.2, random_state=42
        )
        
        # Train Placement Model (GradientBoosting)
        self.placement_model = GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42
        )
        self.placement_model.fit(X_train, y_train_p)
        
        # Train Salary Model (RandomForest) - only on placed students
        X_salary = X_train[y_train_p == 1] if len(X_train[y_train_p == 1]) > 0 else X_train
        y_salary_train = y_salary.loc[y_train_p[y_train_p == 1].index] if len(X_salary) > 0 else [0]
        
        if len(X_salary) > 5:  # Need minimum samples
            self.salary_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.salary_model.fit(X_salary, y_salary_train)
        
        # Scale features
        self.scaler.fit(X)
        self.is_trained = True
        
        # Model performance
        placement_pred = self.placement_model.predict(X_test)
        accuracy = accuracy_score(y_test_p, placement_pred)
        
        print(f"Placement Model Accuracy: {accuracy:.2%}")
        print(f"Salary Model Ready: {self.salary_model is not None}")
    
    def predict_placement(self, scores: Dict[str, float], student_id: str = "STU001") -> Dict:
        """Predict placement probability and generate scorecard"""
        if not self.is_trained:
            return self.rule_based_prediction(scores, student_id)
        
        # Prepare feature vector
        features = np.array([[
            scores.get('cgpa', 7.0),
            scores.get('technical_score', 50),
            scores.get('communication_score', 50),
            scores.get('behavioral_score', 50),
            scores.get('cognitive_score', 50),
            scores.get('resume_score', 50)
        ]])
        
        features_scaled = self.scaler.transform(features)
        placement_prob = self.placement_model.predict_proba(features_scaled)[0][1] * 100
        
        # Salary prediction
        if self.salary_model and placement_prob > 30:
            salary_pred = self.salary_model.predict(features_scaled)[0]
        else:
            salary_pred = 0
        
        overall_score = scores.get('overall_score', 
            0.35 * scores.get('technical_score', 0) +
            0.20 * scores.get('communication_score', 0) +
            0.20 * scores.get('behavioral_score', 0) +
            0.15 * scores.get('cognitive_score', 0) +
            0.10 * scores.get('resume_score', 0)
        )
        
        return self.generate_scorecard(student_id, scores, placement_prob, salary_pred, overall_score)
    
    def rule_based_prediction(self, scores: Dict[str, float], student_id: str) -> Dict:
        """Fallback rule-based prediction"""
        cgpa = scores.get('cgpa', 7.0)
        technical = scores.get('technical_score', 50)
        communication = scores.get('communication_score', 50)
        behavioral = scores.get('behavioral_score', 50)
        
        weighted_score = (technical * 0.35 + communication * 0.25 + 
                         behavioral * 0.20 + cgpa / 10 * 20)
        
        placement_prob = min(weighted_score * 1.2, 95)
        
        return self.generate_scorecard(student_id, scores, placement_prob, 0, weighted_score)
    
    def generate_scorecard(self, student_id: str, scores: Dict, 
                          placement_prob: float, salary: float, overall: float) -> Dict:
        """Generate comprehensive student scorecard"""
        category = "High Placement Chance" if placement_prob >= 75 else \
                  "Moderate Placement Chance" if placement_prob >= 50 else \
                  "Needs Improvement"
        
        roles = self.recommend_roles(scores)
        gaps = self.identify_skill_gaps(scores)
        
        return {
            "student_id": student_id,
            "overall_employability_score": round(overall, 1),
            "placement_probability": round(placement_prob, 1),
            "predicted_salary_lpa": round(salary, 1),
            "category": category,
            "recommended_roles": roles,
            "skill_gaps": gaps,
            "score_breakdown": {
                "cgpa": scores.get('cgpa', 0),
                "technical": scores.get('technical_score', 0),
                "communication": scores.get('communication_score', 0),
                "behavioral": scores.get('behavioral_score', 0),
                "cognitive": scores.get('cognitive_score', 0),
                "resume": scores.get('resume_score', 0)
            },
            "percentiles": self.calculate_percentiles(overall)
        }
    
    def recommend_roles(self, scores: Dict) -> List[str]:
        """Intelligent role recommendations"""
        technical = scores.get('technical_score', 0)
        communication = scores.get('communication_score', 0)
        
        roles = []
        if technical >= 75:
            roles.extend(["Data Scientist", "ML Engineer", "Software Engineer"])
        elif technical >= 65:
            roles.extend(["Data Analyst", "Full Stack Developer"])
        if communication >= 70:
            roles.append("Business Analyst")
        if technical >= 55:
            roles.append("QA Engineer")
            
        return roles[:3] or ["Entry Level Developer"]
    
    def identify_skill_gaps(self, scores: Dict) -> List[str]:
        """Identify skill improvement areas"""
        gaps = []
        thresholds = {
            "technical_score": (65, "Technical Skills"),
            "communication_score": (60, "Communication"),
            "resume_score": (60, "Resume Quality"),
            "behavioral_score": (60, "Behavioral Skills")
        }
        
        for key, (threshold, label) in thresholds.items():
            if scores.get(key, 0) < threshold:
                gaps.append(label)
        
        return gaps
    
    def calculate_percentiles(self, overall_score: float) -> Dict:
        """Calculate percentile ranks"""
        # Simulated percentiles based on score
        percentile = min(overall_score * 1.5, 99)
        return {
            "employability_percentile": round(percentile, 1),
            "batch_rank": f"Top {100-percentile:.0f}%"
        }

def main():
    predictor = PlacementPredictor()
    
    print("PLACEMENT PREDICTOR v3.0 - ML Powered (Phase 5)")
    print("=" * 70)
    
    # Generate and train on synthetic dataset
    print("1️⃣ Generating synthetic dataset...")
    data = predictor.generate_synthetic_dataset(1000)
    predictor.train_models(data)
    
    # Test prediction
    print("\n2️⃣ Testing ML Prediction:")
    test_scores = {
        'cgpa': 8.5,
        'technical_score': 82,
        'communication_score': 75,
        'behavioral_score': 78,
        'cognitive_score': 85,
        'resume_score': 80
    }
    
    scorecard = predictor.predict_placement(test_scores, "STU001")
    
    print("\n" + "="*50)
    print("STUDENT SCORECARD")
    print("="*50)
    print(f"Student ID: {scorecard['student_id']}")
    print(f"Overall Score:  {scorecard['overall_employability_score']}/100")
    print(f"Placement Prob: {scorecard['placement_probability']}%")
    print(f"Salary (LPA):   ₹{scorecard['predicted_salary_lpa']}")
    print(f"Category:       {scorecard['category']}")
    print(f"Percentile:     {scorecard['percentiles']['employability_percentile']}%")
    print(f"Roles:          {', '.join(scorecard['recommended_roles'])}")
    print(f"Gaps:           {', '.join(scorecard['skill_gaps']) if scorecard['skill_gaps'] else 'None'}")
    print("="*50)
    
    # Save models
    joblib.dump(predictor, 'placement_predictor.pkl')
    print("\n Models saved as 'placement_predictor.pkl'")
    print("\n Phase 5 Complete - ML Production Ready!")

if __name__ == "__main__":
    main()
