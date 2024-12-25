from src.questions.abstract_question import QuestionWithLLM
from src.questions.people.board_question import BoardMembersQuestion
from src.questions.business_operation_location import BuisnessLocationQuestion
from src.questions.clients_question import ClientsQuestion
from src.questions.financials.financial_question_bs import FinancialIndicatorQuestionBS
from src.questions.financials.financial_question_is import FinancialIndicatorQuestionIS
from src.questions.general_financial_information import (
    GeneralFinancialInformationQuestion,
)
from src.questions.general_information_question import GeneralInformationQuestion
from src.questions.financials.key_financials import MultipleFinancialIndicatorsQuestions
from src.questions.people.management_team_question import ManagementTeamQuestion
from src.questions.parent_company import ParentCompanyQuestion
from src.questions.people.people_with_linkedIn_question import QuestionWithLinkedin
from src.questions.competitors_question import CompetitorsQuestion
from src.questions.major_announcements_question import MajorAnnouncementQuestion
from src.questions.media_review_question import MediaReviewQuestion
from src.questions.spendcube.spendcube_analysis import SpendCubeQuestion
from src.questions.scandals_or_legal_issues_question import ScandalsQuestion
from src.document_loaders.pdf_loader import PdfLoader
from typing import List
import pandas as pd


def generate_list_of_questions(company_name, pdf_path, csv_path):
    """
    Generate a list of different types of questions related to a company.

    Args:
    - company_name (str): The name of the company.
    - pdf_path (str): The path to the Factiva file.
    - csv_path (str): The path to the Spendcube file.

    Returns:
    - List[Question]: A list of different question instances.
    """
    factiva_loader = PdfLoader([pdf_path])
    question_is = FinancialIndicatorQuestionIS(company_name, factiva_loader)
    question_bs = FinancialIndicatorQuestionBS(company_name, factiva_loader)
    board = BoardMembersQuestion(company_name, factiva_loader)
    management = ManagementTeamQuestion(company_name, factiva_loader)
    return [
        SpendCubeQuestion(
            company_name,
            csv_path=csv_path,
        ),
        MediaReviewQuestion(company_name),
        MajorAnnouncementQuestion(company_name),
        ScandalsQuestion(company_name),
        GeneralInformationQuestion(company_name, factiva_loader),
        QuestionWithLinkedin(company_name, board, management),
        ClientsQuestion(company_name, factiva_loader),
        BuisnessLocationQuestion(company_name, factiva_loader),
        ParentCompanyQuestion(company_name, factiva_loader),
        CompetitorsQuestion(company_name, factiva_loader),
        MultipleFinancialIndicatorsQuestions(
            company_name,
            question_is,
            question_bs,
            pdf_path=pdf_path,
        ),
        GeneralFinancialInformationQuestion(company_name, factiva_loader),
    ]


def generate_small_list_of_questions(company_name, pdf_path, csv_path):
    """
    Generate a smaller list of questions related to a company.

    Args:
    - company_name (str): The name of the company.
    - pdf_path (str): The path to the PDF file.
    - csv_path (str): The path to the CSV file.

    Returns:
    - List[Question]: A smaller list of question instances.
    """
    factiva_loader = PdfLoader([pdf_path])
    question_is = FinancialIndicatorQuestionIS(company_name, factiva_loader)
    question_bs = FinancialIndicatorQuestionBS(company_name, factiva_loader)
    return [
        SpendCubeQuestion(
            company_name,
            csv_path=csv_path,
        ),
        ScandalsQuestion(company_name),
        MultipleFinancialIndicatorsQuestions(
            company_name,
            question_is,
            question_bs,
            pdf_path=pdf_path,
        ),
    ]


def build_report(questions: List[QuestionWithLLM], company_name, html_file):
    """
    Build an HTML report using a list of questions.

    Args:
    - questions (List[QuestionWithLLM]): A list of questions.
    - company_name (str): The name of the company.
    - html_file (str): The path to the HTML file to be created.
    """
    html_file_path = html_file
    with open(html_file_path, "w") as html_file:
        html_file.write("<html>\n<body>\n")
        html_file.write(
            '<h1 style="color: #003883;">'
            + "Market Research on "
            + company_name
            + "</h1>\n"
        )
        for question in questions:
            question.write(html_file)


def aggregate_spendcube_files_and_get_all_vendors_names(paths, company_name):
    """
    Aggregate SpendCube files and get a list of unique vendor names related to a company.

    Args:
    - paths (List[str]): List of file paths.
    - company_name (str): The name of the company.

    Returns:
    - Tuple[pd.DataFrame, List[str]]: A tuple containing aggregated data and a list of unique vendor names.
    """
    data = pd.DataFrame()
    for path in paths:
        yearly_data = pd.read_excel(path, engine="openpyxl")
        regex_pattern = rf"\b{company_name}\b"
        filtered_data = yearly_data[
            yearly_data["supplier_name"].str.contains(
                regex_pattern, case=False, regex=True
            )
        ]
        data = pd.concat([data, filtered_data])
    unique_values_list = data["supplier_name"].unique().tolist()
    return data, unique_values_list


def aggregate_spendcube_files(paths, list_of_entities):
    """
    Aggregate SpendCube files given a list of entities.

    Args:
    - paths (List[str]): List of file paths.
    - list_of_entities (List[str]): List of entities to filter SpendCube data.

    Returns:
    - pd.DataFrame: Aggregated data based on the provided entities.
    """
    data = pd.DataFrame()
    for path in paths:
        yearly_data = pd.read_excel(path, engine="openpyxl")
        filtered_data = yearly_data[
            yearly_data["supplier_name"]
            .str.lower()
            .isin(map(str.lower, list_of_entities))
        ]
        data = pd.concat([data, filtered_data])
    return data
