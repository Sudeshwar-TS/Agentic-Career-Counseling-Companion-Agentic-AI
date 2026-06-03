from agents.langchain_compat import RunnableLambda


def recommend(payload: dict) -> list[dict]:
    student_skills = {skill.lower() for skill in payload["skills"]}
    careers = payload["careers"]
    ranked = []
    for career in careers:
        required = [skill.strip() for skill in career.required_skills.split(",")]
        matched = [skill for skill in required if skill.lower() in student_skills]
        skill_score = len(matched) / max(len(required), 1)
        score = round((skill_score * 0.65) + (career.demand_score * 0.35), 2)
        ranked.append(
            {
                "career_id": career.id,
                "title": career.title,
                "domain": career.domain,
                "description": career.description,
                "required_skills": required,
                "matched_skills": matched,
                "fit_score": score,
                "demand_score": career.demand_score,
                "salary_range": career.salary_range,
                "reason": f"{career.title} is recommended because it matches {len(matched)} required skills and has strong market demand.",
            }
        )
    return sorted(ranked, key=lambda item: item["fit_score"], reverse=True)


career_recommendation_agent = RunnableLambda(recommend)
