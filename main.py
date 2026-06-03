from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from agents.orchestrator import AgentOrchestrator
from config import settings
from database import Base, SessionLocal, engine, get_db
from models import Career, LearningPlan, Skill, Student, User
from rag.counselor import CareerCounselorRAG
from schemas import ChatIn, LoginIn, ProgressIn, RegisterIn
from security import create_token, hash_password, read_token, verify_password
from seed import seed

app = FastAPI(title="CareerNav AI MVP", version="1.0.0")
auth = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings().cors_origin, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed()


def current_user(credentials: HTTPAuthorizationCredentials = Depends(auth), db: Session = Depends(get_db)) -> User:
    email = read_token(credentials.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def current_student(user: User, db: Session) -> Student:
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


def student_skill_names(student: Student) -> list[str]:
    return [skill.name for skill in student.skills]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(name=payload.name, email=str(payload.email), password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    db.add(Student(user_id=user.id))
    db.commit()
    return {"access_token": create_token(user.email), "token_type": "bearer"}


@app.post("/auth/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token(user.email), "token_type": "bearer"}


@app.get("/me")
def me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    return {
        "id": student.id,
        "name": user.name,
        "email": user.email,
        "institution": student.institution,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "career_goal": student.career_goal,
        "progress_percent": student.progress_percent,
        "skills": [{"id": skill.id, "name": skill.name, "proficiency": skill.proficiency, "verified": skill.verified} for skill in student.skills],
    }


@app.post("/resume/upload")
async def upload_resume(file: UploadFile, user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    student.resume_text = text
    result = AgentOrchestrator().extract_profile(text)
    existing = {skill.name.lower() for skill in student.skills}
    for skill_name in result["skills"]:
        if skill_name.lower() not in existing:
            db.add(Skill(student_id=student.id, name=skill_name, proficiency=0.65, verified=False))
    db.commit()
    return {"filename": file.filename, "skills": result["skills"], "message": "Resume parsed successfully"}


@app.get("/careers")
def careers(db: Session = Depends(get_db)):
    return db.query(Career).order_by(Career.demand_score.desc()).all()


@app.get("/recommendations")
def recommendations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    careers = db.query(Career).all()
    return AgentOrchestrator().recommend_careers(student_skill_names(student), careers)


@app.get("/skill-gap/{career_id}")
def skill_gap(career_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    return AgentOrchestrator().skill_gap(student_skill_names(student), career)


@app.get("/roadmap/{career_id}")
def roadmap(career_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    gap = AgentOrchestrator().skill_gap(student_skill_names(student), career)
    plan = AgentOrchestrator().roadmap(gap)
    serialized = "\n".join(f"{item['week']}: {item['title']} - {'; '.join(item['tasks'])}" for item in plan["milestones"])
    db.add(LearningPlan(student_id=student.id, career_id=career.id, title=f"{career.title} Roadmap", milestones=serialized))
    db.commit()
    return plan


@app.get("/internships/{career_id}")
def internships(career_id: int, db: Session = Depends(get_db)):
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    return [
        {"title": f"{career.title} Intern", "organization": "IBM SkillsBuild Partner Network", "location": "Remote", "match_score": 0.92, "deadline": "2026-08-30"},
        {"title": "AI Project Intern", "organization": "University Innovation Lab", "location": "Hybrid", "match_score": 0.86, "deadline": "2026-09-15"},
        {"title": "Product Engineering Intern", "organization": "Startup Accelerator", "location": "Remote", "match_score": 0.8, "deadline": "2026-10-01"},
    ]


@app.post("/chat")
def chat(payload: ChatIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    context = f"Name: {user.name}. Goal: {student.career_goal}. CGPA: {student.cgpa}. Skills: {', '.join(student_skill_names(student))}."
    return CareerCounselorRAG().answer(payload.question, context)


@app.get("/progress")
def get_progress(user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    return {"progress_percent": student.progress_percent, "status": "on_track" if student.progress_percent >= 50 else "needs_focus"}


@app.post("/progress")
def update_progress(payload: ProgressIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    student = current_student(user, db)
    student.progress_percent = max(0, min(100, payload.progress_percent))
    db.commit()
    return {"progress_percent": student.progress_percent, "status": "updated"}
