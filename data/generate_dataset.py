# data/generate_dataset.py - ENHANCED VERSION (Phase 5 ML Ready)
import csv
import random
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict
import os

def generate_realistic_dataset(num_students: int = 2000, save_path: str = "data/students_enhanced.csv") -> pd.DataFrame:
    """Generate comprehensive synthetic dataset for ML training"""
    print(f"Generating {num_students} realistic student records...")
    
    students = []
    np.random.seed(42)  # Reproducible results
    random.seed(42)
    
    # Indian college names and degrees
    institutions = [
        "IIT Madras", "IIT Bombay", "IIT Delhi", "IIT Kanpur", "IIT Kharagpur",
        "NIT Trichy", "VIT Vellore", "SRM Chennai", "Anna University",
        "IIT Hyderabad", "BITS Pilani", "DTU Delhi", "NSIT Delhi"
    ]
    
    degrees = ["B.Tech CSE", "B.Tech ECE", "B.Tech ME", "B.E CSE", "B.Sc Data Science", 
              "BCA", "B.Tech IT", "B.Tech AI&ML"]
    
    for i in range(1, num_students + 1):
        # Personal info
        student_id = f"STU{i:04d}"
        name = f"Student_{random.randint(1000, 9999)}_{i}"
        institution = random.choice(institutions)
        degree = random.choice(degrees)
        graduation_year = random.choice([2025, 2026, 2027])
        cgpa = round(np.clip(np.random.normal(7.5, 1.2), 4.0, 10.0), 1)
        
        # Skill scores with realistic correlations
        technical_base = np.clip(np.random.normal(65, 20), 20, 100)
        technical_score = round(technical_base, 1)
        
        communication_score = round(np.clip(technical_base * 0.7 + np.random.normal(0, 15), 20, 100), 1)
        behavioral_score = round(np.clip(technical_base * 0.6 + np.random.normal(0, 18), 20, 100), 1)
        cognitive_score = round(np.clip(np.random.normal(70, 15), 20, 100), 1)
        resume_score = round(np.clip(technical_base * 0.8 + np.random.normal(0, 12), 20, 100), 1)
        
        # Overall employability score
        overall_score = round(
            technical_score * 0.35 +
            communication_score * 0.20 +
            behavioral_score * 0.20 +
            cognitive_score * 0.15 +
            resume_score * 0.10, 1
        )
        
        # Psychometric scores (Big-5 derived)
        extraversion = round(np.clip(np.random.normal(60, 15), 0, 100), 1)
        conscientiousness = round(np.clip(np.random.normal(70, 12), 0, 100), 1)
        behavioral_ml_score = round((conscientiousness * 0.5 + extraversion * 0.3 + overall_score * 0.2), 1)
        
        # Placement prediction logic (realistic)
        placement_prob = min(
            (overall_score / 100) * 0.7 +
            (cgpa / 10) * 0.2 +
            (technical_score / 100) * 0.1 +
            random.uniform(-0.05, 0.05), 1.0
        )
        
        is_placed = 1 if random.random() < placement_prob else 0
        
        # Salary prediction (LPA - Indian market)
        if is_placed:
            base_salary = 4.5  # Average fresher salary
            salary = round(np.clip(
                base_salary + 
                (cgpa - 7.0) * 0.5 +
                (technical_score - 60) * 0.1 +
                random.uniform(-1.0, 2.0), 2.5, 25.0
            ), 1)
            
            # Role assignment based on scores
            if technical_score >= 85 and cgpa >= 8.5:
                role = random.choice(["Data Scientist", "ML Engineer", "SDE-II"])
            elif technical_score >= 75:
                role = random.choice(["Software Engineer", "Data Analyst", "Full Stack Developer"])
            elif communication_score >= 75:
                role = random.choice(["Business Analyst", "Product Analyst"])
            else:
                role = random.choice(["QA Engineer", "Technical Support", "Junior Developer"])
        else:
            salary = 0.0
            role = "Not Placed"
        
        # Additional ML features
        experience_months = random.choices([0, 6, 12, 18, 24], 
                                         weights=[0.6, 0.2, 0.1, 0.05, 0.05])[0]
        projects_count = random.choices([0, 1, 2, 3, 5], 
                                      weights=[0.3, 0.3, 0.25, 0.1, 0.05])[0]
        
        students.append({
            'student_id': student_id,
            'name': name,
            'institution': institution,
            'degree': degree,
            'graduation_year': graduation_year,
            'cgpa': cgpa,
            'technical_score': technical_score,
            'communication_score': communication_score,
            'behavioral_score': behavioral_score,
            'cognitive_score': cognitive_score,
            'resume_score': resume_score,
            'psychometric_behavioral': behavioral_ml_score,
            'overall_score': overall_score,
            'experience_months': experience_months,
            'projects_count': projects_count,
            'is_placed': is_placed,
            'salary_lpa': salary,
            'role': role,
            'placement_prob': round(placement_prob * 100, 1)
        })
    
    df = pd.DataFrame(students)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Save comprehensive dataset
    df.to_csv(save_path, index=False)
    print(f"Saved {len(df)} records to {save_path}")
    
    return df

def print_dataset_summary(df: pd.DataFrame):
    """Enhanced dataset statistics"""
    print("\n DATASET SUMMARY")
    print("=" * 50)
    print(f"Total Students:     {len(df):,}")
    print(f"Placed Students:    {df['is_placed'].sum():,}")
    print(f"Placement Rate:     {df['is_placed'].mean():.1%}")
    print(f"Avg CGPA:           {df['cgpa'].mean():.1f}")
    print(f"Avg Overall Score:  {df['overall_score'].mean():.1f}")
    print(f"Avg Salary (LPA):   ₹{df['salary_lpa'][df['is_placed']==1].mean():.1f}")
    
    print("\n TOP PERFORMERS")
    top_students = df.nlargest(5, 'overall_score')[['student_id', 'overall_score', 'salary_lpa', 'role']]
    print(top_students.to_string(index=False))
    
    print("\n INSTITUTION WISE")
    print(df.groupby('institution')['is_placed'].agg(['count', 'mean']).round(3))
    
    print("\n ROLE DISTRIBUTION")
    print(df[df['is_placed']==1]['role'].value_counts().head())

def generate_ml_features(save_path: str = "data/students_ml_ready.csv"):
    """Generate ML-optimized dataset"""
    df = generate_realistic_dataset(5000, save_path)
    print_dataset_summary(df)
    
    # Additional ML-ready features
    df['technical_communication_balance'] = df['technical_score'] / df['communication_score']
    df['cgpa_overall_ratio'] = df['cgpa'] * 10 / df['overall_score']
    
    df.to_csv(save_path.replace('.csv', '_ml_ready.csv'), index=False)
    print(f"\n🔬 ML-ready dataset saved: {save_path.replace('.csv', '_ml_ready.csv')}")

if __name__ == "__main__":
    print("ENHANCED DATASET GENERATOR v2.0 - Phase 5 ML Ready")
    print("=" * 60)
    
    # Generate datasets
    generate_ml_features("data/students_enhanced.csv")
    
    # Quick sample
    print("\n SAMPLE RECORDS")
    df_sample = pd.read_csv("data/students_enhanced.csv").head()
    print(df_sample[['student_id', 'cgpa', 'overall_score', 'is_placed', 'salary_lpa', 'role']].to_string(index=False))
    
    print("\n Dataset ready for ML training!")
    print("Compatible with placement_model.py")
