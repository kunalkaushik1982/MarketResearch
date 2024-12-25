import json
import os
import pandas as pd
from src.questions.abstract_question import AbstractQuestion
from src.questions.financials.financial_question_bs import FinancialIndicatorQuestionBS
from src.questions.financials.financial_question_is import FinancialIndicatorQuestionIS
from src.utils.custom_errors import RetrievingError


json_path = os.path.join(os.getcwd(), "src/questions/financials", "alerts_config.json")
alerts_params = json.load(open(json_path))


class MultipleFinancialIndicatorsQuestions(AbstractQuestion):
    def __init__(
        self,
        company_name,
        questionBS: FinancialIndicatorQuestionBS,
        questionIS: FinancialIndicatorQuestionIS,
        pdf_path,
    ):
        self.company_name = company_name
        self.questionBS = questionBS
        self.questionIS = questionIS
        self.pdf_path = pdf_path

    def write(self, html_file):
        try:
            html_file.write(
                '<h4 style="color: #d30473;font-size: 110%;">'
                + self.build_global_table().to_html(
                    escape=False, classes="center", justify="center"
                )
                + f"<br>The displayed figures are all in {self.questionBS.unit}. "
                + "<br>Figures highlighted in red indicate concerning aspect "
                + f"regarding {self.company_name}'s financial health."
                + "</h4>\n"
            )
            html_file.write(
                '<h4 style="color: #d30473;font-size: 110%;">'
                + self._get_source()
                + "</h4>\n"
            )
        except RetrievingError as e:
            html_file.write(
                '<h4 style="color: #d30473;font-size: 110%;">' + e.__str__() + "</h4>\n"
            )

    def build_global_table(self) -> pd.DataFrame:
        table_BS = self._convert_to_numerical_table(self.questionBS.answer_as_dict)
        table_IS = self._convert_to_numerical_table(self.questionIS.answer_as_dict)
        merged_table = pd.concat([table_BS, table_IS], axis=1)
        merged_table_ratios = self._add_ratio(merged_table)
        highlighted_table = self._highlight_table(merged_table_ratios.round(2))
        return highlighted_table

    def _convert_to_numerical_table(self, answer: json) -> pd.DataFrame:
        df = pd.DataFrame(
            {key: value for key, value in answer.items() if key != "Unit"}
        )
        df.set_index("Year", inplace=True)
        df = df.applymap(
            lambda x: float(x.replace(",", "").replace("(", "-").replace(")", ""))
            if "(" in x and ")" in x
            else float(x.replace(",", ""))
        )
        return df

    def _add_ratio(self, table):
        table["Debt-to-Equity Ratio"] = (
            table["Total Liabilities"] / table["Total Shareholders Equity"]
        )
        table["Current Ratio"] = (
            table["Total Current Assets"] / table["Total Current Liabilities"]
        )
        table["Return on Equity (ROE)"] = (
            table["Total Liabilities"] / table["Total Current Liabilities"]
        )
        table["Operating Profit Margin"] = (
            table["Net Income"] / table["Total Shareholders Equity"]
        )
        table["Net Profit margin"] = (
            table["Operating Income"] / table["Net Sales or Revenue"]
        )
        return table

    def _highlight_table(self, table):
        for col in alerts_params["decreasing_alert"]["column_names"]:
            table[col] = table[col].apply(
                lambda x: self._highlight_decreasing_column(x, table[col])
            )
        for alert in alerts_params["ratio_lower_than_value_alerts"]:
            for col in alert["column_names"]:
                table[col] = table[col].apply(
                    lambda x: self._highlight_ratios(x, alert["threshold"])
                )
        return table

    def _highlight_decreasing_column(
        self,
        val,
        entire_column,
    ):
        year = entire_column[entire_column == val].index[0]
        next_val = (
            entire_column.loc[year - 1] if year > entire_column.index.min() else None
        )
        if next_val is not None and val < next_val:
            return (
                f'<span style="color: red" '
                f'title="This figure is lower than the previous year which might be concerning">'
                f"{val}"
                f"</span>"
            )
        else:
            return val

    def _highlight_ratios(self, val, threshold):
        if val < threshold:
            return f'<span style="color: red" title="This ratio is lower than {threshold} which might be concerning">{val}</span>'
        else:
            return val

    def _get_source(self):
        return "Source: " + os.path.basename(self.pdf_path)
