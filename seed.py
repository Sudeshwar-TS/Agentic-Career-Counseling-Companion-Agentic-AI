import json
from pathlib import Path

from database import Base, SessionLocal, engine
from models import Career, Skill, Student, User
from security import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        careers = json.loads(Path("data/careers.json").read_text(encoding="utf-8"))
        for item in careers:
            if not db.query(Career).filter(Career.title == item["title"]).first():
                db.add(Career(**item))
        if not db.query(User).filter(User.email == "student@demo.com").first():
            user = User(name="Demo Student", email="student@demo.com", password_hash=hash_password("Password123"))
            db.add(user)
            db.flush()
            student = Student(user_id=user.id, cgpa=8.4, career_goal="AI Engineer", resume_text="Python SQL machine learning React FastAPI cloud project")
            db.add(student)
            db.flush()
            for name, proficiency in [("Python", 0.85), ("SQL", 0.72), ("Machine Learning", 0.7), ("React", 0.62), ("FastAPI", 0.6)]:
                db.add(Skill(student_id=student.id, name=name, proficiency=proficiency, verified=True))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
