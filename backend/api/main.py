"""
FastAPI backend for Employability AI.

Demo-first behavior:
- No paid API key required.
- Uses a local JSON store under `data/demo_store.json`.
- ML engines are optional; endpoints fall back safely if deps are missing.
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add project root to Python path (run from anywhere)
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from backend.services.demo_store import get_interview_result, get_resume_analysis, set_interview_result, set_resume_analysis  # noqa: E402
from backend.services.repository import (  # noqa: E402
    add_test_attempt,
    get_scores,
    get_student,
    get_test_history,
    set_component_score,
    upsert_student,
)
from backend.services.interview_engine import evaluate_interview, generate_questions  # noqa: E402
from backend.services.scorecard_service import build_scorecard  # noqa: E402

try:  # optional engines
    from backend.services.psychometric import PsychometricEngine  # noqa: E402
    from ml.nlp.resume_scorer import ResumeScorer  # noqa: E402

    psychometric_engine = PsychometricEngine()
    resume_scorer = ResumeScorer()
except Exception:
    psychometric_engine = None
    resume_scorer = None

app = FastAPI(title="Employability AI (Demo)", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class StudentUpsertRequest(BaseModel):
    student_id: str = Field(default="STU001")
    name: str = Field(default="Ravi Kumar")
    email: Optional[str] = Field(default="ravi@example.com")
    cgpa: Optional[float] = Field(default=8.1, ge=0.0, le=10.0)


class SubmitTestRequest(BaseModel):
    student_id: str = Field(default="STU001")
    test_id: str
    responses: Dict[str, Any] = Field(default_factory=dict)
    duration_seconds: Optional[float] = 0.0
    variant: Optional[str] = None


class InterviewStartRequest(BaseModel):
    student_id: str = Field(default="STU001")
    count: int = Field(default=5, ge=3, le=10)


class InterviewSubmitRequest(BaseModel):
    student_id: str = Field(default="STU001")
    eye_contact_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    duration_seconds: float = Field(default=0.0, ge=0.0)
    answered_count: int = Field(default=0, ge=0)
    total_questions: int = Field(default=0, ge=0)


@app.get("/")
async def home():
    return {"message": "Employability AI API (Demo)", "docs": "http://localhost:8000/docs"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "demo_store": True,
        "engines": {"psychometric_engine": psychometric_engine is not None, "resume_scorer": resume_scorer is not None},
    }


@app.post("/api/student/upsert")
async def upsert_student_api(req: StudentUpsertRequest):
    return upsert_student(req.model_dump())


@app.get("/api/tests")
async def list_tests():
    return {
        "tests": [
            {
                "id": "psychometric",
                "name": "Behavioural & Personality Assessment",
                "type": "psychometric",
                "description": "Measures personality traits, work style and behavioural tendencies",
                "questions": 10,
                "marks": 50,
            },
            {
                "id": "communication",
                "name": "Communication Skills Assessment",
                "type": "communication",
                "description": "Tests English, grammar, vocabulary and verbal communication",
                "questions": 10,
                "marks": 20,
            },
            {
                "id": "cognitive",
                "name": "Cognitive Ability Assessment",
                "type": "cognitive",
                "description": "Tests logical reasoning, aptitude and problem solving",
                "questions": 10,
                "marks": 20,
            },
            {
                "id": "technical",
                "name": "Technical Skills Assessment",
                "type": "technical",
                "description": "Role-based technical test (choose your target job role)",
                "questions": 10,
                "marks": 20,
            },
        ]
    }


TECHNICAL_VARIANTS = {
    "python": {
        "label": "Python / General",
        "questions": [
            {"id": "t1", "question": "What is a Python list?", "options": ["Mutable sequence", "Immutable sequence", "Database", "Compiler"], "answer": 0},
            {"id": "t2", "question": "Which keyword defines a function in Python?", "options": ["func", "def", "lambda", "define"], "answer": 1},
            {"id": "t3", "question": "Time complexity of binary search is:", "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"], "answer": 1},
            {"id": "t4", "question": "SQL stands for:", "options": ["Structured Query Language", "Simple Query Language", "System Query Logic", "None"], "answer": 0},
            {"id": "t5", "question": "In OOP, encapsulation means:", "options": ["Hiding data + methods together", "Multiple inheritance", "Only abstraction", "Only polymorphism"], "answer": 0},
            {"id": "t6", "question": "Which is NOT a Python data type?", "options": ["tuple", "set", "arraylist", "dict"], "answer": 2},
            {"id": "t7", "question": "HTTP status for 'Not Found' is:", "options": ["200", "401", "404", "500"], "answer": 2},
            {"id": "t8", "question": "Git command to create a new branch:", "options": ["git branch <name>", "git fork", "git clone", "git init"], "answer": 0},
            {"id": "t9", "question": "REST APIs commonly use which format?", "options": ["YAML", "JSON", "INI", "TXT"], "answer": 1},
            {"id": "t10", "question": "Which is a SQL aggregate function?", "options": ["WHERE", "GROUP", "COUNT", "ORDER"], "answer": 2},
        ],
    },
    "web": {
        "label": "Web Developer",
        "questions": [
            {"id": "tw1", "question": "Which HTML tag is used to create a hyperlink?", "options": ["<link>", "<a>", "<href>", "<url>"], "answer": 1},
            {"id": "tw2", "question": "In CSS, which property changes text color?", "options": ["font-style", "color", "background", "text"], "answer": 1},
            {"id": "tw3", "question": "Which method converts JSON string to object in JavaScript?", "options": ["JSON.parse()", "JSON.stringify()", "toJSON()", "parseJSON()"], "answer": 0},
            {"id": "tw4", "question": "What does HTTP status code 301 mean?", "options": ["Not Found", "Unauthorized", "Moved Permanently", "Server Error"], "answer": 2},
            {"id": "tw5", "question": "In React, state should be updated using:", "options": ["Direct assignment", "setState / state setter", "document.getElementById", "window.state"], "answer": 1},
            {"id": "tw6", "question": "Which is true about localStorage?", "options": ["Cleared on tab close", "Stores data as strings", "Only works on server", "Expires in 5 mins"], "answer": 1},
            {"id": "tw7", "question": "Which HTTP method is typically used to create a resource?", "options": ["GET", "POST", "PUT", "DELETE"], "answer": 1},
            {"id": "tw8", "question": "CORS is mainly related to:", "options": ["Database indexing", "Cross-origin requests", "File compression", "Caching"], "answer": 1},
            {"id": "tw9", "question": "Which is a valid CSS selector for a class named 'card'?", "options": ["#card", ".card", "card()", "@card"], "answer": 1},
            {"id": "tw10", "question": "What is the purpose of a build step in React apps?", "options": ["Run SQL migrations", "Bundle/minify assets", "Create database tables", "Start the OS"], "answer": 1},
        ],
    },
    "data": {
        "label": "Data Analyst",
        "questions": [
            {"id": "td1", "question": "In pandas, which function reads a CSV file?", "options": ["read.csv()", "pd.read_csv()", "pd.load_csv()", "import_csv()"], "answer": 1},
            {"id": "td2", "question": "Which SQL clause is used to filter rows?", "options": ["WHERE", "GROUP BY", "ORDER BY", "JOIN"], "answer": 0},
            {"id": "td3", "question": "Which aggregation returns the number of rows?", "options": ["SUM()", "COUNT()", "AVG()", "MAX()"], "answer": 1},
            {"id": "td4", "question": "What is the shape of a DataFrame?", "options": ["Rows and columns", "Only columns", "Only rows", "File size"], "answer": 0},
            {"id": "td5", "question": "Which chart is best for showing distribution?", "options": ["Histogram", "Pie chart", "Radar chart", "Map"], "answer": 0},
            {"id": "td6", "question": "What does NULL mean in SQL?", "options": ["Zero", "Empty string", "Missing/unknown value", "False"], "answer": 2},
            {"id": "td7", "question": "In Python, NumPy is mainly used for:", "options": ["Web pages", "Numerical arrays", "Email sending", "GUI design"], "answer": 1},
            {"id": "td8", "question": "A primary key should be:", "options": ["Duplicate", "Null", "Unique", "A text file"], "answer": 2},
            {"id": "td9", "question": "What is overfitting (basic ML)?", "options": ["Model too simple", "Model memorizes training data", "No training data", "No features"], "answer": 1},
            {"id": "td10", "question": "Which is a common metric for classification?", "options": ["Accuracy", "MSE", "MAE", "RMSE"], "answer": 0},
        ],
    },
    "devops": {
        "label": "DevOps / Cloud",
        "questions": [
            {"id": "to1", "question": "What does CI stand for?", "options": ["Continuous Integration", "Computer Interface", "Central Instance", "Code Injection"], "answer": 0},
            {"id": "to2", "question": "Docker is mainly used for:", "options": ["Virtualizing UI", "Containerizing applications", "Writing SQL", "Editing images"], "answer": 1},
            {"id": "to3", "question": "Which file commonly defines Docker build steps?", "options": ["docker.yml", "Dockerfile", "compose.json", "build.txt"], "answer": 1},
            {"id": "to4", "question": "In Linux, which command lists files?", "options": ["ls", "dir", "show", "list"], "answer": 0},
            {"id": "to5", "question": "Kubernetes is used for:", "options": ["Running unit tests", "Orchestrating containers", "Designing UIs", "Writing emails"], "answer": 1},
            {"id": "to6", "question": "What is an environment variable used for?", "options": ["Store config/secrets at runtime", "Compress files", "Change CPU speed", "Replace source code"], "answer": 0},
            {"id": "to7", "question": "Which port is HTTPS by default?", "options": ["80", "21", "443", "8080"], "answer": 2},
            {"id": "to8", "question": "A 'health check' endpoint is used to:", "options": ["Monitor service status", "Delete logs", "Reset DB", "Upload files"], "answer": 0},
            {"id": "to9", "question": "What does IaC stand for?", "options": ["Infrastructure as Code", "Interface as Code", "Instance at Cloud", "Internet as Cache"], "answer": 0},
            {"id": "to10", "question": "Which tool is commonly used for provisioning cloud resources?", "options": ["Terraform", "Photoshop", "Excel", "Figma"], "answer": 0},
        ],
    },
    "java": {
        "label": "Java Developer",
        "questions": [
            {"id": "tj1", "question": "Which keyword is used to inherit a class in Java?", "options": ["inherits", "extends", "implements", "super"], "answer": 1},
            {"id": "tj2", "question": "Which collection does NOT allow duplicates?", "options": ["List", "Set", "ArrayList", "Vector"], "answer": 1},
            {"id": "tj3", "question": "JVM stands for:", "options": ["Java Variable Machine", "Java Virtual Machine", "Joint Version Manager", "Java Vendor Module"], "answer": 1},
            {"id": "tj4", "question": "Which access modifier is most restrictive?", "options": ["public", "protected", "private", "default"], "answer": 2},
            {"id": "tj5", "question": "What does 'static' mean for a method?", "options": ["Belongs to class", "Belongs to object only", "Runs faster", "Cannot return value"], "answer": 0},
            {"id": "tj6", "question": "Which is used to handle exceptions?", "options": ["try/catch", "if/else", "switch", "loop"], "answer": 0},
            {"id": "tj7", "question": "Which interface represents a map of key/value pairs?", "options": ["List", "Map", "Set", "Queue"], "answer": 1},
            {"id": "tj8", "question": "Which is true about String in Java?", "options": ["Mutable", "Immutable", "Only numeric", "Only boolean"], "answer": 1},
            {"id": "tj9", "question": "Which keyword creates a new object?", "options": ["new", "make", "create", "alloc"], "answer": 0},
            {"id": "tj10", "question": "What does 'implements' indicate?", "options": ["Class inheritance", "Interface implementation", "Package import", "Thread start"], "answer": 1},
        ],
    },
}


def _strip_answers(questions):
    return [{k: v for k, v in q.items() if k != "answer"} for q in questions]


def _technical_variant_key(variant: Optional[str]) -> str:
    key = (variant or "python").strip().lower()
    return key if key in TECHNICAL_VARIANTS else "python"


def _answer_key_from_questions(questions):
    return {str(q.get("id")): int(q.get("answer")) for q in questions if q.get("id") is not None and q.get("answer") is not None}


@app.get("/api/tests/{test_id}/questions")
async def get_test_questions(test_id: str, variant: Optional[str] = None):
    test_id = test_id.lower()
    if test_id == "psychometric" and psychometric_engine is not None:
        questions = psychometric_engine.get_questions(num_questions=10)
        return {"test_id": test_id, "format": "likert", "questions": questions}

    if test_id == "technical":
        key = _technical_variant_key(variant)
        v = TECHNICAL_VARIANTS[key]
        return {"test_id": test_id, "variant": key, "variant_label": v["label"], "format": "mcq", "questions": _strip_answers(v["questions"])}

    bank = {
        "cognitive": [
            {"id": "c1", "question": "2, 4, 8, 16, ?", "options": ["18", "24", "32", "64"], "answer": 2},
            {"id": "c2", "question": "If 3 workers finish in 6 days, 6 workers finish in:", "options": ["3 days", "6 days", "12 days", "9 days"], "answer": 0},
            {"id": "c3", "question": "Find the odd one: Circle, Triangle, Square, Cube", "options": ["Circle", "Triangle", "Square", "Cube"], "answer": 3},
            {"id": "c4", "question": "A is to Z as B is to:", "options": ["Y", "X", "Z", "A"], "answer": 0},
            {"id": "c5", "question": "If today is Monday, 10 days later is:", "options": ["Tuesday", "Wednesday", "Thursday", "Friday"], "answer": 2},
            {"id": "c6", "question": "Simplify: 15% of 200", "options": ["15", "20", "25", "30"], "answer": 3},
            {"id": "c7", "question": "Next number: 1, 1, 2, 3, 5, ?", "options": ["7", "8", "9", "10"], "answer": 1},
            {"id": "c8", "question": "If x=2, evaluate: 3x^2", "options": ["6", "8", "12", "16"], "answer": 2},
            {"id": "c9", "question": "Find the missing: 5, 10, 20, 40, ?", "options": ["45", "60", "70", "80"], "answer": 3},
            {"id": "c10", "question": "Odd one: Apple, Mango, Banana, Carrot", "options": ["Apple", "Mango", "Banana", "Carrot"], "answer": 3},
        ],
        "communication": [
            {"id": "cm1", "question": "Best way to handle a customer complaint:", "options": ["Interrupt", "Listen and clarify", "Ignore", "Argue"], "answer": 1},
            {"id": "cm2", "question": "A good email subject line is:", "options": ["Clear and specific", "Very long", "All caps", "Blank"], "answer": 0},
            {"id": "cm3", "question": "In a meeting, you should:", "options": ["Be prepared", "Multitask", "Interrupt", "Be late"], "answer": 0},
            {"id": "cm4", "question": "When you don't know an answer, you should:", "options": ["Guess confidently", "Say you will check and follow up", "Change topic", "Blame others"], "answer": 1},
            {"id": "cm5", "question": "Good active listening includes:", "options": ["Nodding and summarizing", "Looking away", "Checking phone", "Interrupting"], "answer": 0},
            {"id": "cm6", "question": "Professional tone means:", "options": ["Respectful and concise", "Rude", "Too casual", "Very emotional"], "answer": 0},
            {"id": "cm7", "question": "If two teammates disagree, you should:", "options": ["Discuss calmly", "Avoid", "Shout", "Stop working"], "answer": 0},
            {"id": "cm8", "question": "Best practice for presentations:", "options": ["Speak clearly", "Read only slides", "Rush", "Avoid eye contact"], "answer": 0},
            {"id": "cm9", "question": "Feedback is best received by:", "options": ["Listening and improving", "Rejecting", "Arguing", "Ignoring"], "answer": 0},
            {"id": "cm10", "question": "When messaging, you should:", "options": ["Use clear sentences", "Use only emojis", "Use slang always", "Be vague"], "answer": 0},
        ],
    }

    if test_id not in bank:
        raise HTTPException(status_code=404, detail="Unknown test_id")

    questions = _strip_answers(bank[test_id])
    return {"test_id": test_id, "format": "mcq", "questions": questions}


@app.post("/api/tests/submit")
async def submit_test(req: SubmitTestRequest):
    test_id = req.test_id.lower()

    if test_id == "psychometric" and psychometric_engine is not None:
        parsed = {}
        for k, v in req.responses.items():
            try:
                parsed[int(k)] = int(v)
            except Exception:
                continue
        result = psychometric_engine.score_responses(parsed, student_id=req.student_id)
        behavioral = float(getattr(result, "behavioral_score", 0.0))
        set_component_score(req.student_id, "behavioral", behavioral)

        if hasattr(result, "model_dump"):  # pydantic v2
          raw = result.model_dump(mode="json")
        elif hasattr(result, "dict"):  # pydantic v1
          raw = result.dict()
        else:
          raw = result

        add_test_attempt(
            req.student_id,
            {
                "test_id": test_id,
                "test_name": "Behavioural & Personality Assessment",
                "type": "psychometric",
                "score": behavioral,
                "status": "Passed" if behavioral >= 60 else "Needs Improvement",
                "raw": raw,
            },
        )
        return {"ok": True, "component": "behavioral", "score": behavioral, "scores": get_scores(req.student_id)}

    answer_keys = {
        "cognitive": {"c1": 2, "c2": 0, "c3": 3, "c4": 0, "c5": 2, "c6": 3, "c7": 1, "c8": 2, "c9": 3, "c10": 3},
        "communication": {"cm1": 1, "cm2": 0, "cm3": 0, "cm4": 1, "cm5": 0, "cm6": 0, "cm7": 0, "cm8": 0, "cm9": 0, "cm10": 0},
    }

    if test_id == "technical":
        key = _technical_variant_key(req.variant)
        answer_keys["technical"] = _answer_key_from_questions(TECHNICAL_VARIANTS[key]["questions"])

    if test_id not in answer_keys:
        raise HTTPException(status_code=400, detail="Unsupported test_id")

    correct = 0
    total = 0
    for qid, chosen in req.responses.items():
        if qid not in answer_keys[test_id]:
            continue
        total += 1
        try:
            if int(chosen) == int(answer_keys[test_id][qid]):
                correct += 1
        except Exception:
            continue

    score = round((correct / total * 100.0) if total else 0.0, 1)

    # "Resume/NLP" slot in screenshot uses this bucket; keep it simple for demo.
    component_map = {"technical": "technical", "cognitive": "cognitive", "communication": "resume"}
    component = component_map[test_id]
    set_component_score(req.student_id, component, score)

    name_map = {
        "technical": "Technical Skills Assessment",
        "cognitive": "Cognitive Ability Assessment",
        "communication": "Communication Skills Assessment",
    }

    raw = {"correct": correct, "total": total}
    if test_id == "technical":
        key = _technical_variant_key(req.variant)
        raw["variant"] = key
        raw["variant_label"] = TECHNICAL_VARIANTS[key]["label"]
    add_test_attempt(
        req.student_id,
        {
            "test_id": test_id,
            "test_name": name_map[test_id],
            "type": test_id,
            "score": score,
            "status": "Passed" if score >= 60 else "Needs Improvement",
            "raw": raw,
        },
    )

    return {"ok": True, "component": component, "score": score, "scores": get_scores(req.student_id)}


@app.get("/api/tests/history/{student_id}")
async def test_history(student_id: str):
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"student": student, "history": get_test_history(student_id)}


@app.post("/api/resume/analyze")
async def analyze_resume(student_id: str = "STU001", target_role: Optional[str] = None, file: UploadFile = File(...)):
    content = await file.read()
    try:
        text = content.decode("utf-8", errors="ignore")
    except Exception:
        text = ""

    if resume_scorer is None:
        analysis = {"student_id": student_id, "resume_score": 50.0, "recommended_roles": [], "skill_gaps": ["Add Projects"]}
    else:
        analysis = resume_scorer.score_resume(text, student_id=student_id, target_role=target_role)

    set_resume_analysis(student_id, text, analysis)
    set_component_score(student_id, "resume", float(analysis.get("resume_score", 0.0)))
    return {"ok": True, "analysis": analysis}


@app.get("/api/scorecard/{student_id}")
async def get_scorecard(student_id: str):
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    scores = get_scores(student_id)
    resume_analysis = get_resume_analysis(student_id)
    sc = build_scorecard(student_id, scores, cgpa=student.get("cgpa"), resume_analysis=resume_analysis)
    last_interview = get_interview_result(student_id)
    return {"student": student, "scorecard": sc.to_dict(), "last_interview": last_interview}


@app.post("/api/interview/start")
async def start_interview(req: InterviewStartRequest):
    resume_analysis = get_resume_analysis(req.student_id)
    return {"student_id": req.student_id, "questions": generate_questions(resume_analysis, count=req.count)}


@app.post("/api/interview/submit")
async def submit_interview(req: InterviewSubmitRequest):
    result = evaluate_interview(
        eye_contact_ratio=req.eye_contact_ratio,
        duration_seconds=req.duration_seconds,
        answered_count=req.answered_count,
        total_questions=req.total_questions,
    )
    set_interview_result(req.student_id, result)
    set_component_score(req.student_id, "video_ai", float(result["video_ai_score"]))
    return {"ok": True, "result": result, "scores": get_scores(req.student_id)}


class TrainModelRequest(BaseModel):
    n_samples: int = Field(default=1000, ge=200, le=20000)


@app.post("/api/model/train")
async def train_model(req: TrainModelRequest):
    """
    Train (or re-train) the placement predictor using a synthetic dataset.
    Saves to `placement_predictor.pkl` at the project root.
    """
    try:
        from ml.predictive.placement_model import PlacementPredictor  # type: ignore
        import joblib  # type: ignore

        predictor = PlacementPredictor()
        data = predictor.generate_synthetic_dataset(req.n_samples)
        predictor.train_models(data)

        out_path = project_root / "placement_predictor.pkl"
        joblib.dump(predictor, str(out_path))
        return {"ok": True, "saved_to": str(out_path), "trained": True, "n_samples": req.n_samples}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
