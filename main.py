import argparse
import langchain
from src.utils.questions_and_report_utils import (
    generate_list_of_questions,
    build_report,
)

langchain.debug = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process company data")
    parser.add_argument("--company", type=str, help="Name of the company")

    args = parser.parse_args()
    if args.company:
        company_name = args.company
    else:
        print("Please provide a company name using --company")
        exit(1)

    csv_path = "SpendReport/Spend Report Gartner 2019-2023(June).xlsx"
    pdf_path = "factiva/Gartner Inc Factiva Report.pdf"
    questions = generate_list_of_questions(company_name, pdf_path, csv_path)

    build_report(questions, company_name, f"{company_name}.html")
