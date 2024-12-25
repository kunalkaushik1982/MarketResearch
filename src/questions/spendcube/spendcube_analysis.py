from src.questions.abstract_question import AbstractQuestion
import pandas as pd
import plotly.express as px
import os


class SpendCubeQuestion(AbstractQuestion):
    """
    Represents a question related to spend reports from SpendCube for a given company.
    """

    def __init__(self, company_name, csv_path):
        """
        Initializes a SpendCubeQuestion object.

        Args:
        - company_name (str): Name of the company.
        - csv_path (str): Path to the CSV file containing spending data.
        """
        self.company_name = company_name
        self.path = csv_path
        self.data = pd.read_excel(csv_path, engine="openpyxl")

    def write(self, html_file):
        """
        Writes spending-related information into an HTML file.

        Args:
        - html_file: File object for writing HTML content.
        """
        html_file.write(
            '<h4 style="color: #d30473;font-size: 110%;">'
            + self._get_spending_data()
            + "</h4>\n"
        )

        html_file.write(
            '<h4 style="color: #d30473;font-size: 110%;">'
            + self._get_spending_data_graph().to_html(
                full_html=False, default_height=400, default_width=600
            )
            + "</h4>\n"
        )

        html_file.write(
            '<h4 style="color: #d30473;font-size: 110%;">'
            + "Here are the purchasers on Publicis side with their respective spending in euros: "
            + self._get_table_vendors_or_purchasers("segment_code_and_text").to_html(
                classes="table table-stripped",
                index=False,
                justify="center",
            )
            + "</h4>\n"
        )
        html_file.write(
            '<h4 style="color: #d30473;font-size: 110%;">'
            + f"Here are the purchasers of vendors on {self.company_name} side "
            + "with their respective spending in euros: "
            + self._get_table_vendors_or_purchasers("supplier_name").to_html(
                classes="table table-stripped",
                index=False,
                justify="center",
            )
            + "</h4>\n"
        )
        html_file.write(
            '<h4 style="color: #d30473;font-size: 110%;">'
            + self._get_source()
            + "</h4>\n"
        )
        html_file.write("</h4>\n")

    def _get_spending_data(self):
        """
        Generates spending data summary for the company across fiscal years.

        Returns:
        - str: Annual spending data for each year.
        """
        grouped_data = self.data.groupby("fiscal_year")["spend_in_eur"].sum().round(2)
        result_strings = [
            f"<br> In {fiscal_year}, the amount spent with {self.company_name}"
            + f"was {'{:,}'.format(spend_in_eur).replace(',', ' ')} euros"
            for fiscal_year, spend_in_eur in grouped_data.items()
        ]
        return "\n".join(result_strings)

    def _get_spending_data_graph(self):
        """
        Generates a bar graph of spending data across fiscal years.

        Returns:
        - Plotly figure: Bar graph displaying spending data.
        """
        grouped_data = self.data.groupby("fiscal_year")["spend_in_eur"].sum().round(2)
        fig = px.bar(
            grouped_data,
            x=grouped_data.index,
            y="spend_in_eur",
            labels={"x": "Fiscal Year", "y": "Amount Spent (in Euros)"},
            title=f"Spending amount with {self.company_name} by year",
        )
        return fig

    def _get_table_vendors_or_purchasers(self, entity):
        """
        Returns a list of purchasers on the company's side with spending details.

        Returns:
        - pandas DataFrame: List of purchasers with their spending details.
        """
        pivoted_df = self.data.pivot_table(
            index=entity,
            columns="fiscal_year",
            values="spend_in_eur",
            aggfunc="sum",
        )
        pivoted_df = pivoted_df.fillna(0)

        pivoted_df["total_spend"] = pivoted_df.sum(axis=1)
        pivoted_df = pivoted_df.sort_values(by="total_spend", ascending=False)
        pivoted_df.reset_index(inplace=True)

        for col in pivoted_df.columns:
            if col != entity:
                pivoted_df[col] = pivoted_df[col].apply(
                    lambda x: f"{x:,.0f}".replace(",", " ")
                )
        new_df = pd.DataFrame(
            data=pivoted_df.values, columns=pivoted_df.columns.tolist()
        )
        return new_df

    def _get_source(self):
        """
        Retrieves the data source information.

        Returns:
        - str: Information about the source of spending data.
        """
        return "Source: " + os.path.basename(self.path)
