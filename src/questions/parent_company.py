from src.document_loaders.serp_loader import SerpLoader
from src.questions.abstract_question import QuestionWithLLM


class ParentCompanyQuestion(QuestionWithLLM):
    def __init__(self, company_name, loader, backup_loaders=[]):
        title = f"Does {company_name} have a parent company?"
        prompt = f"""
        Can you provide information on whether {company_name} has a parent company,
        and if so, what is the name of the parent company?
        """
        llm_model = "gpt4"
        if backup_loaders == []:
            backup_loaders.append(self._build_serp_loader(company_name))

        super().__init__(title, prompt, loader, llm_model, backup_loaders)

    def _build_serp_loader(self, company_name):
        serp_prompts = [
            f"{company_name} parent company",
        ]
        return SerpLoader(serp_prompts)
