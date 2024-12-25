import unittest
from src.document_loaders.serp_loader import SerpLoader
from src.questions.abstract_question import QuestionWithLLM
from src.document_loaders.pdf_loader import PdfLoader


class TestReportGeneration(unittest.TestCase):
    def setUp(self) -> None:
        company_name = "Gartner"
        pdf_path = "factiva/Gartner Inc Factiva Report.pdf"
        factiva_loader = PdfLoader([pdf_path])
        title_question_with_answer_in_factiva = (
            f"In what year was founded {company_name}?"
        )
        prompt_question_with_answer_in_factiva = f"""
            Extract {company_name} date of creation
            """
        title_question_with_no_answer_in_factiva = (
            f"In what year was founded the company named Amazon?"
        )
        prompt_question_with_no_answer_in_factiva = f"""
            Extract Amazon year of creation
            """
        llm_model = "gpt4"
        backup_loaders_question_with_answer_in_factiva = [
            SerpLoader(
                [
                    f"{company_name} latest news",
                ]
            )
        ]
        backup_loaders_prompt_question_with_no_answer_in_factiva = [
            SerpLoader(
                [
                    f"Amazon date of creation",
                ]
            )
        ]
        self.question_with_answer_in_factiva = QuestionWithLLM(
            title_question_with_answer_in_factiva,
            prompt_question_with_answer_in_factiva,
            factiva_loader,
            llm_model,
            backup_loaders_question_with_answer_in_factiva,
        )
        self.question_with_no_answer_in_factiva = QuestionWithLLM(
            title_question_with_no_answer_in_factiva,
            prompt_question_with_no_answer_in_factiva,
            factiva_loader,
            llm_model,
            backup_loaders_prompt_question_with_no_answer_in_factiva,
        )

    def test_relevant_answer_in_pdf(self):
        answer = self.question_with_answer_in_factiva.answer_json["answer"]
        self.assertIn("1979", answer)

    def test_relevant_source_pdf(self):
        sources = self.question_with_answer_in_factiva.sources
        self.assertIn("factiva/Gartner Inc Factiva Report", sources[0])

    def test_relevant_answer_in_google(self):
        answer = self.question_with_no_answer_in_factiva.answer_json["answer"]
        self.assertIn("1994", answer)

    def test_sources_not_empty_serper(self):
        self.assertGreaterEqual(len(self.question_with_no_answer_in_factiva.sources), 1)


if __name__ == "__main__":
    unittest.main()
