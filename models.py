from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    student: Mapped["Student"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    institution: Mapped[str] = mapped_column(String(160), default="IBM SkillsBuild AICTE College")
    branch: Mapped[str] = mapped_column(String(120), default="Computer Science")
    cgpa: Mapped[float] = mapped_column(Float, default=8.0)
    career_goal: Mapped[str] = mapped_column(String(160), default="AI Engineer")
    resume_text: Mapped[str] = mapped_column(Text, default="")
    progress_percent: Mapped[float] = mapped_column(Float, default=20)
    user: Mapped[User] = relationship(back_populates="student")
    skills: Mapped[list["Skill"]] = relationship(back_populates="student", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    proficiency: Mapped[float] = mapped_column(Float, default=0.6)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    student: Mapped[Student] = relationship(back_populates="skills")


class Career(Base):
    __tablename__ = "careers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[str] = mapped_column(Text, nullable=False)
    demand_score: Mapped[float] = mapped_column(Float, default=0.8)
    salary_range: Mapped[str] = mapped_column(String(120), default="8-18 LPA")


class LearningPlan(Base):
    __tablename__ = "learning_plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.id"))
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    milestones: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
