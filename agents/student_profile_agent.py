import re

from agents.langchain_compat import RunnableLambda

SKILLS = [
    "Python",
    "JavaScript",
    "React",
    "Tailwind CSS",
    "FastAPI",
    "SQLite",
    "SQL",
    "Machine Learning",
    "Deep Learning",
    "LangChain",
    "ChromaDB",
    "Cloud",
    "Docker",
    "Git",
    "Data Visualization",
    "Statistics",
    "Security",
]


def extract_skills_from_text(text: str) -> list[str]:
    found = []
    for skill in SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            found.append(skill)
    aliases = {"ml": "Machine Learning", "ai": "Machine Learning", "js": "JavaScript"}
    lowered = text.lower()
    for alias, skill in aliases.items():
        if re.search(rf"\b{alias}\b", lowered) and skill not in found:
            found.append(skill)
    return found


student_profile_agent = RunnableLambda(lambda payload: {"skills": extract_skills_from_text(payload.get("resume_text", ""))})
