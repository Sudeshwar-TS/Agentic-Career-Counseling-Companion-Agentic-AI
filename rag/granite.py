from functools import cached_property

from config import settings


class GraniteLLM:
    @cached_property
    def model(self):
        cfg = settings()
        if not cfg.watsonx_api_key or not cfg.watsonx_project_id:
            return None
        from langchain_ibm import WatsonxLLM

        return WatsonxLLM(
            model_id=cfg.granite_model_id,
            url=cfg.watsonx_url,
            apikey=cfg.watsonx_api_key,
            project_id=cfg.watsonx_project_id,
            params={"decoding_method": "greedy", "max_new_tokens": 500, "temperature": 0.2},
        )

    def invoke(self, prompt: str) -> str:
        if self.model is None:
            return (
                "CareerNav AI recommends focusing on verified skills, one deployed portfolio project, a role-specific "
                "learning roadmap, and internships aligned with your target career. Add IBM SkillsBuild credentials "
                "and practice interview explanations for each project."
            )
        return str(self.model.invoke(prompt)).strip()
