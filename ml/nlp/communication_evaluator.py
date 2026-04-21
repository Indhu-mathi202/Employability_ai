# ml/nlp/communication_evaluator.py - FIXED (No NLTK required)
import sys
import os
import re
from typing import Dict, List, Optional
from collections import Counter
from datetime import datetime

# Fix import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Communication quality metrics
POSITIVE_WORDS = {
    'excellent', 'great', 'strong', 'proficient', 'expert', 'experienced', 
    'passionate', 'dedicated', 'team', 'collaborate', 'achieved', 'delivered',
    'success', 'results', 'impact', 'led', 'managed', 'developed', 'skill', 'skills'
}

NEGATIVE_WORDS = {
    'weak', 'poor', 'limited', 'basic', 'struggle', 'difficulty', 'failed',
    'problem', 'issue', 'error', 'mistake'
}

GOOD_CONNECTORS = [
    'therefore', 'however', 'furthermore', 'consequently', 'additionally',
    'moreover', 'thus', 'hence', 'also', 'besides', 'meanwhile', 'firstly', 'secondly'
]

FILLER_WORDS = [
    'um', 'uh', 'like', 'you know', 'basically', 'literally', 'actually',
    'sort of', 'kind of', 'i mean', 'you see', 'well'
]

PROFESSIONAL_PHRASES = [
    'team player', 'problem solver', 'fast learner', 'detail oriented',
    'hard working', 'quick learner', 'results driven', 'self motivated'
]

class CommunicationEvaluator:
    """Advanced Communication Assessment - No external dependencies"""
    
    def __init__(self):
        self.stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'you', 'your', 'yours',
            'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its', 'they', 'them',
            'their', 'what', 'which', 'who', 'whom', 'this', 'that', 'these',
            'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall',
            'should', 'may', 'might', 'must', 'can', 'the', 'a', 'an', 'and',
            'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at',
            'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up',
            'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very'
        }
    
    def simple_sent_tokenize(self, text: str) -> List[str]:
        """Simple sentence tokenizer without NLTK"""
        # Split on . ! ? followed by space or newline
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def simple_word_tokenize(self, text: str) -> List[str]:
        """Simple word tokenizer without NLTK"""
        # Split on whitespace and punctuation
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        return [w for w in words if w not in self.stop_words and len(w) > 2]
    
    def preprocess_text(self, text: str) -> tuple:
        """Clean and tokenize text (NLTK-free)"""
        if not text or len(text.strip()) < 3:
            return "", [], []
        
        text = text.lower().strip()
        sentences = self.simple_sent_tokenize(text)
        words = self.simple_word_tokenize(text)
        return text, sentences, words
    
    def analyze_readability(self, text: str, sentences: List[str]) -> Dict:
        """Simple readability analysis"""
        words = self.simple_word_tokenize(text)
        word_count = len(words)
        sentence_count = len(sentences)
        
        if sentence_count == 0:
            return {"readability_score": 0, "grade_level": 0, "avg_sentence_length": 0}
        
        avg_sentence_length = word_count / sentence_count
        
        # Simple grade level estimation
        avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
        grade_level = min((avg_sentence_length * 0.3 + avg_word_length * 0.4), 20)
        
        # Readability score (higher = easier)
        readability = max(100 - (grade_level * 4), 0)
        
        return {
            "readability_score": round(readability, 1),
            "grade_level": round(grade_level, 1),
            "avg_sentence_length": round(avg_sentence_length, 1)
        }
    
    def analyze_sentiment(self, words: List[str]) -> Dict:
        """Sentiment analysis using word polarity"""
        total_words = len(words)
        if total_words == 0:
            return {"sentiment_score": 0, "positivity": 0}
        
        positive_count = sum(1 for word in words if word in POSITIVE_WORDS)
        negative_count = sum(1 for word in words if word in NEGATIVE_WORDS)
        
        positivity = positive_count / total_words
        sentiment = (positive_count - negative_count) / total_words
        
        return {
            "sentiment_score": round(sentiment * 100, 1),
            "positive_words": positive_count,
            "negative_words": negative_count,
            "positivity_ratio": round(positivity * 100, 1)
        }
    
    def analyze_structure(self, sentences: List[str], text: str) -> Dict:
        """Analyze text structure and professionalism"""
        text_lower = text.lower()
        has_intro = any(phrase in text_lower for phrase in ['i am', 'my name', "i'm"])
        has_experience = any(phrase in text_lower for phrase in ['experience', 'worked', 'project'])
        has_goals = any(phrase in text_lower for phrase in ['goal', 'aim', 'want', 'career'])
        
        professional_count = sum(1 for phrase in PROFESSIONAL_PHRASES if phrase in text_lower)
        connector_count = sum(text_lower.count(connector) for connector in GOOD_CONNECTORS)
        filler_count = sum(text_lower.count(filler) for filler in FILLER_WORDS)
        
        structure_score = (
            (20 if has_intro else 0) +
            (25 if has_experience else 0) +
            (20 if has_goals else 0) +
            min(professional_count * 8, 20) +
            min(connector_count * 3, 10)
        )
        
        return {
            "structure_score": min(structure_score, 85),
            "has_intro": has_intro,
            "has_experience": has_experience,
            "has_goals": has_goals,
            "professional_phrases": professional_count,
            "connectors_used": connector_count,
            "fillers_used": filler_count
        }
    
    def analyze_vocabulary(self, words: List[str]) -> Dict:
        """Vocabulary analysis"""
        total_words = len(words)
        unique_words = len(set(words))
        vocab_richness = unique_words / total_words if total_words > 0 else 0
        
        tech_words = {'python', 'sql', 'data', 'machine', 'learning', 'analysis', 'project', 'team'}
        tech_count = sum(1 for word in words if word in tech_words)
        tech_ratio = tech_count / total_words if total_words > 0 else 0
        
        return {
            "vocab_richness": round(vocab_richness * 100, 1),
            "unique_words": unique_words,
            "tech_vocab_ratio": round(tech_ratio * 100, 1)
        }
    
    def evaluate(self, text: str, student_id: str = "STU001") -> Dict:
        """Complete communication evaluation"""
        if not text or len(text.strip()) < 20:
            return {
                "communication_score": 0.0,
                "student_id": student_id,
                "issues": ["Text too short"],
                "total_words": 0
            }
        
        clean_text, sentences, words = self.preprocess_text(text)
        total_words = len(self.simple_word_tokenize(clean_text))
        
        readability = self.analyze_readability(clean_text, sentences)
        sentiment = self.analyze_sentiment(words)
        structure = self.analyze_structure(sentences, clean_text)
        vocabulary = self.analyze_vocabulary(words)
        
        # Calculate total score
        score_components = {
            "readability": min(readability["readability_score"], 25),
            "sentiment": max(sentiment["sentiment_score"] + 50, 0),
            "structure": structure["structure_score"],
            "vocabulary": vocabulary["vocab_richness"]
        }
        
        filler_penalty = min(structure["fillers_used"] * 10, 15)
        total_score = sum(score_components.values())
        total_score = max(total_score - filler_penalty, 0)
        total_score = min(total_score, 100)
        
        return {
            "communication_score": round(total_score, 2),
            "student_id": student_id,
            "total_words": total_words,
            "total_sentences": len(sentences),
            "readability": readability,
            "sentiment": sentiment,
            "structure": structure,
            "vocabulary": vocabulary,
            "strengths": [s for s in [
                "Clear structure" if structure["structure_score"] > 60 else "",
                "Positive tone" if sentiment["sentiment_score"] > 10 else "",
                "Good vocabulary" if vocabulary["vocab_richness"] > 50 else ""
            ] if s],
            "improvements": [i for i in [
                "Avoid filler words" if structure["fillers_used"] > 0 else "",
                "Add more structure" if structure["structure_score"] < 50 else ""
            ] if i]
        }

if __name__ == "__main__":
    evaluator = CommunicationEvaluator()
    
    print("COMMUNICATION EVALUATOR v2.1 - NO NLTK REQUIRED")
    print("=" * 60)
    
    test_texts = [
        """Hi, I'm Madhan, a final year Computer Science student with strong Python skills. 
        I have worked on machine learning projects and data analysis using pandas and SQL. 
        Furthermore, I have excellent communication skills and love working in teams. 
        My goal is to become a data scientist and solve real-world problems.""",
        
        """um like I know python and stuff, I did some projects I think, 
        you know SQL also maybe, basically I'm good at coding I guess.""",
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n Test {i}:")
        result = evaluator.evaluate(text, f"STU00{i}")
        
        print(f"   Score: {result['communication_score']}/100")
        print(f"   Words: {result['total_words']} | Sentences: {result['total_sentences']}")
        print(f"   Strengths: {', '.join(result['strengths']) if result['strengths'] else 'Developing'}")
    
    print("\n FIXED - Runs perfectly without NLTK!")
