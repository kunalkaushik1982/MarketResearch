import re
import pandas as pd
from src.document_loaders.serp_loader import SerpLoader
from src.questions.abstract_question import AbstractQuestion
from src.questions.people.board_question import BoardMembersQuestion
from src.questions.people.management_team_question import ManagementTeamQuestion
from src.utils.custom_errors import RetrievingError


class QuestionWithLinkedin(AbstractQuestion):
    def __init__(
        self,
        company_name,
        board: BoardMembersQuestion,
        management: ManagementTeamQuestion,
    ):
        self.company_name = company_name
        self.board = board
        self.management = management

    def write(self, html_file):
        try:
            if not (self.management._check_answer()):
                self.management._switch_retriever_and_reset()

            self._write_table(html_file, self.management)

            if not (self.board._check_answer()):
                self.board._switch_retriever_and_reset()

            self._write_table(html_file, self.board)

        except RetrievingError as e:
            html_file.write(
                '<h4 style="color: #d30473;font-size: 110%;">' + e.__str__() + "</h4>\n"
            )

    def _write_table(self, html_file, people):
        html_file.write(
            '<h2 style="color: #003883;font-size: 130%;">' + people.title + "</h2>\n"
        )
        html_file.write(
            '<h4 style="color: #d30473;font-size: 110%;">'
            + self._build_table(people).to_html(
                escape=False, classes="center", justify="center"
            )
            + "</h4>\n"
        )
        for source in people.sources[0].split(" ; "):
            html_file.write("<a href=" + source + "> <li>" + source + "</li> </a>")

    def _build_table(self, table_data):
        table = table_data.answer_as_dict
        table["LinkedIn Link"] = [
            self._get_url_linkedIn(name) for name in table["Name"]
        ]
        df = pd.DataFrame(table)
        df["LinkedIn Link"] = df["LinkedIn Link"].apply(
            lambda x: f'<a href="{x}">{x}</a>'
        )
        return df

    def _get_url_linkedIn(self, name):
        url = self._build_serp_loader(name)._get_urls()[0]
        pattern = r"\b\w*linkedin\w*\b"
        matches = re.findall(pattern, url, re.IGNORECASE)
        if matches:
            return url
        else:
            return "Not found"

    def _build_serp_loader(self, name):
        serp_prompts = [f"Linkedin {name} {self.company_name}"]
        return SerpLoader(serp_prompts)
