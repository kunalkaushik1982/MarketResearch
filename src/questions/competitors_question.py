from src.document_loaders.serp_loader import SerpLoader
from src.questions.abstract_question import QuestionWithLLM


class CompetitorsQuestion(QuestionWithLLM):
    def __init__(self, company_name, loader, backup_loaders=[]):
        title = f"Who are the competitors of {company_name}?"
        prompt = f"""
        Please extract the competitors of {company_name} mentionned in the Peer Comparison
        table with their respective sales.
        """
        llm_model = "gpt4"
        if backup_loaders == []:
            backup_loaders.append(self._build_serp_loader(company_name))

        super().__init__(title, prompt, loader, llm_model, backup_loaders)

    def _build_serp_loader(self, company_name):
        serp_prompts = [f"{company_name} main competitors"]
        return SerpLoader(serp_prompts)
