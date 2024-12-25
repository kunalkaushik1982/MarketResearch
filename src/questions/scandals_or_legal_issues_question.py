from src.document_loaders.serp_loader import SerpLoader
from src.questions.abstract_question import QuestionWithLLM


class ScandalsQuestion(QuestionWithLLM):
    def __init__(self, company_name, loader=None):
        title = f"What are the scandals involving {company_name}?"
        prompt = f"""
        Describe ALL scandals (corruption, fraud, controversy, bribery, money laundering, etc.)
        involving {company_name}. Always specify date (year, month, day) and display the scandals chronologically.
      """
        if loader is None:
            loader = self._build_loader(company_name)
        llm_model = "gpt4"
        super().__init__(title, prompt, loader, llm_model)

    def _build_loader(self, company_name):
        serp_prompts = [
            f"{company_name} corruption bribery penalty",
            f"{company_name} modern slavery child labour",
            f"{company_name} money laundering legal issues",
            f"{company_name} Public relations disaster",
            f"{company_name} Lawsuit Investigation",
        ]

        return SerpLoader(serp_prompts)
