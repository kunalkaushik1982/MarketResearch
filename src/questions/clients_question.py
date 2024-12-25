from src.document_loaders.serp_loader import SerpLoader
from src.questions.abstract_question import QuestionWithLLM


class ClientsQuestion(QuestionWithLLM):
    def __init__(self, company_name, loader, backup_loaders=[]):
        title = f"Who are {company_name} clients? "
        prompt = f"""
        What types of individuals and organizations are included among the {company_name}'s clients?
        Give some example of {company_name}'s clients.
        """
        llm_model = "gpt4"
        if backup_loaders == []:
            backup_loaders.append(self._build_serp_loader(company_name))

        super().__init__(title, prompt, loader, llm_model, backup_loaders)

    def _build_serp_loader(self, company_name):
        serp_prompts = [
            f"{company_name} main clients",
            f"{company_name} type of clients",
        ]
        return SerpLoader(serp_prompts)
