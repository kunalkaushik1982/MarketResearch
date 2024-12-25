from src.document_loaders.serp_loader import SerpLoader
from src.questions.abstract_question import QuestionWithLLM
import json

from src.utils.custom_errors import RetrievingError


class FinancialIndicatorQuestionBS(QuestionWithLLM):
    """
    Class to extract KPIs in the annual Balance Sheet (BS) within the Factiva report.
    """

    _answer_as_dict = None
    _unit = None

    def __init__(self, company_name, loader, backup_loaders=[]):
        self.company_name = company_name
        title = ""
        prompt = """
        Please extract from the "Annual Balance Sheet" table the following figures for all years displayed:
        1. Total Assets
        2. Total Current Assets
        3. Total Liabilities
        4. Total Shareholders Equity
        5. Total Current Liabilities

        Provide your answer in a json format.

        Example of answer:
        {{
            'Year': [2022, 2021, 2020],
            'Total Assets': ['3,321.76', '2.7', '6.637'],
            'Total Current Assets': ['3,321.76', '2.7', '12.537'],
            'Total Liabilities': ['3,14.76', '2.1345', '6.637'],
            'Total Shareholders Equity': ['3,34.76', '2.45345', '6.637'],
            'Total Current Liabilities': ['3,1456.76', '2.1345', '6.637']
            'Unit': 'million USD'
        }}

        Be careful to display the unit ONLY in the 'Unit' section as in the example.

"""
        llm_model = "gpt4"
        if backup_loaders == []:
            backup_loaders.append(self._build_serp_loader(company_name))

        super().__init__(title, prompt, loader, llm_model, backup_loaders)

    def _build_serp_loader(self, company_name):
        serp_prompts = [
            f"{company_name} Total Assets, Total Current Assets, "
            "Total Liabilities, Total Shareholders Equity, "
            "Total Current Liabilities"
        ]
        return SerpLoader(serp_prompts)

    @property
    def unit(self):
        if self._unit is None:
            self._unit = self.answer_as_dict["Unit"]
        return self._unit

    @property
    def answer_as_dict(self):
        if self._answer_as_dict is None:
            if not self._check_answer():
                raise RetrievingError(
                    f"The annual Balance Sheet for {self.company_name} is not provided."
                )
            answer: str = self.answer_json["answer"]
            self._answer_as_dict = json.loads(answer.replace("'", '"'))
        return self._answer_as_dict
