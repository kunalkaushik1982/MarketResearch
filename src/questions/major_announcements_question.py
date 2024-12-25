from src.document_loaders.serp_loader import SerpLoader
from src.questions.abstract_question import QuestionWithLLM


class MajorAnnouncementQuestion(QuestionWithLLM):
    def __init__(self, company_name, loader=None):
        title = f"Have there been any major announcements of {company_name}?"
        prompt = f"""
        Have there been any major announcements of {company_name}? Always specify the date (year, month, day)
        """
        llm_model = "gpt4"
        if loader is None:
            loader = self._build_loader(company_name)
        super().__init__(title, prompt, loader, llm_model)

    def _build_loader(self, company_name):
        serp_prompts = [
            f"Press releases {company_name}",
            f"Major announcements {company_name}",
            f"{company_name} newsroom",
        ]
        return SerpLoader(serp_prompts)
