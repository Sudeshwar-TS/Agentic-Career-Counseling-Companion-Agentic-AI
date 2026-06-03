from agents.langchain_compat import RunnableLambda


def analyze_gap(payload: dict) -> dict:
    student_skills = {skill.lower() for skill in payload["skills"]}
    required = [skill.strip() for skill in payload["career"].required_skills.split(",")]
    matched = [skill for skill in required if skill.lower() in student_skills]
    missing = [skill for skill in required if skill.lower() not in student_skills]
    readiness = round(len(matched) / max(len(required), 1), 2)
    return {
        "career_id": payload["career"].id,
        "career_title": payload["career"].title,
        "matched_skills": matched,
        "missing_skills": missing,
        "readiness_score": readiness,
        "summary": "Close missing skills through courses, projects, and interview practice.",
    }


skill_gap_agent = RunnableLambda(analyze_gap)
