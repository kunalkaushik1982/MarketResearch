from src.document_loaders.serp_loader import SerpLoader
from src.questions.abstract_question import QuestionWithLLM


class GeneralInformationQuestion(QuestionWithLLM):
    def __init__(self, company_name, loader, backup_loaders=[]):
        title = f"What is {company_name} and what products or services does it offer?"
        prompt = f"""
        Can you describe {company_name} and specify what it sells
    """
        llm_model = "gpt4"
        if backup_loaders == []:
            backup_loaders.append(self._build_serp_loader(company_name))

        super().__init__(title, prompt, loader, llm_model, backup_loaders)

    def _build_serp_loader(self, company_name):
        serp_prompts = [f"{company_name} company overview"]
        return SerpLoader(serp_prompts)
