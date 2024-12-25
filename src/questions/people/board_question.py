import json
from src.document_loaders.serp_loader import SerpLoader
from src.questions.abstract_question import QuestionWithLLM


class BoardMembersQuestion(QuestionWithLLM):
    _answer_as_dict = None

    def __init__(self, company_name, loader, backup_loaders=[]):
        self.company_name = company_name
        title = f" Who are the members of {company_name}'s Board of directors?"
        prompt = f"""
        Please extract Names in the board of Directors of {company_name} with their respective position title.
        Provide your answer in a json format.

        Example of answer:
        {{
            "Name": ["Elena Adams", "John Doe", "Harry Poker"],
            "Job Title": ["Independant director", "Senior VP-Global Corporate Communications",
            "Chief Executive Officer"],
        }}
        """
        llm_model = "gpt4"
        if backup_loaders == []:
            backup_loaders.append(self._build_serp_loader(company_name))

        super().__init__(title, prompt, loader, llm_model, backup_loaders)

    def _build_serp_loader(self, company_name):
        serp_prompts = [f"{company_name} board members"]
        return SerpLoader(serp_prompts)

    @property
    def answer_as_dict(self):
        if self._answer_as_dict is None:
            answer: str = self.answer_json["answer"]
            self._answer_as_dict = json.loads(answer)
        return self._answer_as_dict
