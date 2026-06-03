from agents.langchain_compat import RunnableLambda


def build_roadmap(payload: dict) -> dict:
    missing = payload.get("missing_skills", [])
    career_title = payload.get("career_title", "Target Career")
    milestones = []
    week = 1
    for skill in missing[:6]:
        milestones.append(
            {
                "week": f"Weeks {week}-{week + 1}",
                "title": f"Learn {skill}",
                "tasks": [
                    f"Complete one beginner-to-intermediate module on {skill}",
                    f"Build a small portfolio task using {skill}",
                    "Update resume and GitHub with evidence",
                ],
            }
        )
        week += 2
    if not milestones:
        milestones = [
            {
                "week": "Weeks 1-2",
                "title": f"Advanced {career_title} capstone",
                "tasks": ["Build a deployed project", "Write a case study", "Practice technical explanation"],
            }
        ]
    return {"career_title": career_title, "duration_weeks": max(4, len(milestones) * 2), "milestones": milestones}


learning_roadmap_agent = RunnableLambda(build_roadmap)
