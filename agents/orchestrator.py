from agents.career_recommendation_agent import career_recommendation_agent
from agents.learning_roadmap_agent import learning_roadmap_agent
from agents.skill_gap_agent import skill_gap_agent
from agents.student_profile_agent import student_profile_agent


class AgentOrchestrator:
    def extract_profile(self, resume_text: str) -> dict:
        return student_profile_agent.invoke({"resume_text": resume_text})

    def recommend_careers(self, skills: list[str], careers) -> list[dict]:
        return career_recommendation_agent.invoke({"skills": skills, "careers": careers})

    def skill_gap(self, skills: list[str], career) -> dict:
        return skill_gap_agent.invoke({"skills": skills, "career": career})

    def roadmap(self, gap: dict) -> dict:
        return learning_roadmap_agent.invoke({"career_title": gap["career_title"], "missing_skills": gap["missing_skills"]})
