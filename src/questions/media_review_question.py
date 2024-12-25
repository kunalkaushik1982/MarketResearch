from src.document_loaders.serp_loader import SerpLoader
from src.questions.abstract_question import QuestionWithLLM


class MediaReviewQuestion(QuestionWithLLM):
    def __init__(self, company_name, loader=None):
        title = f"What do clients say about {company_name}?"
        prompt = f"""
        Give me an overview of the media reviews about {company_name} and always specify the date (year, month, day)
        """
        llm_model = "gpt4"
        if loader is None:
            loader = self._build_loader(company_name)
        super().__init__(title, prompt, loader, llm_model)

    def _build_loader(self, company_name):
        serp_prompts = [
            f"{company_name} media reviews",
            f"{company_name} online reviews",
            f"Client reviews of {company_name}?",
        ]
        return SerpLoader(serp_prompts)
