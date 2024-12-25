import os
import io
import tempfile
import json
from fastapi import FastAPI, File, Form, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Annotated, List, Union
from src.utils.questions_and_report_utils import (
    aggregate_spendcube_files,
    aggregate_spendcube_files_and_get_all_vendors_names,
    build_report,
    generate_list_of_questions,
    generate_small_list_of_questions,
)
import pandas as pd
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from src.utils.azure_strorage_utils import generate_random_string
from fastapi.responses import JSONResponse


json_path = os.path.join(os.getcwd(), "credentials", "credentials.json")
credentials = json.load(open(json_path))
account_name = credentials.get("account_name")
account_key = credentials.get("account_key")

blob_service_client = BlobServiceClient(
    account_url=f"https://{account_name}.blob.core.windows.net",
    credential=account_key,
)

app = FastAPI()

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:7000").split(
    ","
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return "OK"


@app.post("/generateReportfromLocalFiles", response_class=HTMLResponse)
def generateReport(
    factiva_report: Annotated[UploadFile, File()],
    spend_report: Annotated[UploadFile, File()],
    company_name: Annotated[str, Form()],
):
    """
    Endpoint for generating a report based on provided files and company name.

    Args:
    - factiva_report (UploadFile): Uploaded Factiva pdf report file.
    - spend_report (UploadFile): Uploaded spending report xlsx file.
    - company_name (str): Name of the company.

    Returns:
    - HTMLResponse: HTML content of the generated report.
    """
    print(f"Factiva Report received : {factiva_report.filename}")
    print(f"Spend Report received : {spend_report.filename}")
    print(f"Parameter detected for brand : {company_name}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
        temp_pdf_file.write(factiva_report.file.read())
        print(f"Temporary file saved at: {temp_pdf_file.name}")
        pdf_path = temp_pdf_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_xlsx_file:
        temp_xlsx_file.write(spend_report.file.read())
        print(f"Temporary file saved at: {temp_xlsx_file.name}")
        csv_path = temp_xlsx_file.name
    questions = generate_list_of_questions(company_name, pdf_path, csv_path)
    temp_html_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".html")

    build_report(questions, company_name, temp_html_file.name)

    with open(temp_html_file.name, "r") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content, status_code=200)


@app.post(
    "/aggregateSpendcubeFilesandReturnvendorsEntities", response_class=JSONResponse
)
def aggregateSpendcubefilesandReturnvendorsEntities(
    start_year: Annotated[int, Form()],
    end_year: Annotated[int, Form()],
    company_name: Annotated[str, Form()],
    entities_of_interest: Annotated[Union[List[str], None], Query()] = None,
):
    container_client_spend_report = blob_service_client.get_container_client(
        "spendcube"
    )
    spend_cube_paths = []
    for year in range(start_year, end_year + 1):
        try:
            blob_name = f"{year}_SpendCube_Randomised_DATA.xlsm"
            spend_report = container_client_spend_report.download_blob(blob_name)
        except ResourceNotFoundError:
            return JSONResponse(
                content={
                    "response": f"The spendcube file regarding year {year} is not found on Azure",
                    "status": "error",
                }
            )
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".xlsx"
        ) as temp_xlsx_file:
            temp_xlsx_file.write(io.BytesIO(spend_report.readall()).getvalue())
            print(f"Temporary file saved at: {temp_xlsx_file.name}")
            csv_path = temp_xlsx_file.name
            spend_cube_paths.append(csv_path)
    container_client_result = blob_service_client.get_container_client(
        "spendcube-aggregated"
    )
    if entities_of_interest is None:
        (
            aggregated_spend_cube_file,
            entities_of_interest,
        ) = aggregate_spendcube_files_and_get_all_vendors_names(
            spend_cube_paths, company_name
        )
        temp_aggregated_spend_report = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".xlsx"
        )
        with pd.ExcelWriter(
            temp_aggregated_spend_report.name, engine="openpyxl"
        ) as writer:
            aggregated_spend_cube_file.to_excel(writer)
        with open(temp_aggregated_spend_report.name, "rb") as data:
            blob_name = (
                f"Spendcube_aggregated_{company_name}_{start_year}_{end_year}_"
                + generate_random_string(3)
                + ".xlsx"
            )
            container_client_result.upload_blob(name=blob_name, data=data)

        return JSONResponse(
            content={
                "response": f"The spendcube file is aggregated and uploaded on Azure Storage with name: {blob_name}."
                + f"The different vendors involved are: {entities_of_interest}",
                "filename": blob_name,
                "status": "ok",
            }
        )

    else:
        aggregated_spend_cube_file = aggregate_spendcube_files(
            spend_cube_paths, entities_of_interest
        )
        temp_aggregated_spend_report = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".xlsx"
        )
        with pd.ExcelWriter(
            temp_aggregated_spend_report.name, engine="openpyxl"
        ) as writer:
            aggregated_spend_cube_file.to_excel(writer)

        with open(temp_aggregated_spend_report.name, "rb") as data:
            blob_name = (
                f"Spendcube_aggregated_{company_name}_{start_year}_{end_year}_"
                + generate_random_string(3)
                + ".xlsx"
            )
            container_client_result.upload_blob(name=blob_name, data=data)

        return JSONResponse(
            content={
                "response": f"The spendcube file is aggregated and uploaded on Azure Storage with name: {blob_name}."
                + f"The different vendors involved are: {entities_of_interest}",
                "filename": blob_name,
                "status": "ok",
            }
        )


@app.post("/generateReportfromAzure", response_class=JSONResponse)
def generateReportAzure(
    factiva_report_name: Annotated[str, Form()],
    spend_report_name: Annotated[str, Form()],
    company_name: Annotated[str, Form()],
):
    """
    Generate and upload a market research report to Azure Blob Storage.

    Parameters:
    - `factiva_report_name`: Name of the Factiva report.
    - `spend_report_name`: Name of the spend report.
    - `company_name`: Name of the company for market research.

    Returns:
    - `JSONResponse`: Response containing information about the generated report upload.

    This function generates a market research report based on provided Factiva and spend reports
    associated with a specific company. It reads the reports from Azure Blob Storage, processes them,
    generates a list of questions, builds an HTML report, and uploads the generated report to Azure Blob Storage.
    """
    container_client_factiva = blob_service_client.get_container_client("factiva")
    container_client_spend_report = blob_service_client.get_container_client(
        "spendcube-aggregated"
    )
    try:
        factiva_report = container_client_factiva.download_blob(factiva_report_name)
    except ResourceNotFoundError:
        return JSONResponse(
            content={
                "response": "The factiva file is not found on Azure",
                "status": "error",
            }
        )
    try:
        spend_report = container_client_spend_report.download_blob(spend_report_name)
    except ResourceNotFoundError:
        return JSONResponse(
            content={
                "response": "The spendcube file is not found on Azure",
                "status": "error",
            }
        )

    with tempfile.NamedTemporaryFile(
        delete=False, prefix="FactivaReport_", suffix=".pdf"
    ) as temp_pdf_file:
        temp_pdf_file.write(io.BytesIO(factiva_report.readall()).getvalue())
        print(f"Temporary file saved at: {temp_pdf_file.name}")
        pdf_path = temp_pdf_file.name

    with tempfile.NamedTemporaryFile(
        delete=False, prefix="SpendReport_", suffix=".xlsx"
    ) as temp_xlsx_file:
        temp_xlsx_file.write(io.BytesIO(spend_report.readall()).getvalue())
        print(f"Temporary file saved at: {temp_xlsx_file.name}")
        csv_path = temp_xlsx_file.name

    questions = generate_list_of_questions(company_name, pdf_path, csv_path)

    temp_html_report = tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".html"
    )
    build_report(questions, company_name, temp_html_report.name)
    container_client_result = blob_service_client.get_container_client("result")

    with open(temp_html_report.name, "rb") as data:
        blob_name = (
            f"Market_Research_{company_name}_" + generate_random_string(3) + ".html"
        )
        container_client_result.upload_blob(name=blob_name, data=data)

    return JSONResponse(
        content={
            "response": f"The market research is generated and uploaded on Azure Storage with blob name: {blob_name}",
            "filename": blob_name,
            "status": "ok",
        }
    )


@app.post("/generateSmallreportFromazure", response_class=HTMLResponse)
def generateSmallreportAzure(
    factiva_report_name: Annotated[str, Form()],
    spend_report_name: Annotated[str, Form()],
    company_name: Annotated[str, Form()],
):
    """
    Generate a small market research with only 3 questions and upload it on Azure Blob Storage.

    Parameters:
    - `factiva_report_name`: Name of the Factiva report.
    - `spend_report_name`: Name of the spend report.
    - `company_name`: Name of the company for market research.

    Returns:
    - `JSONResponse`: Response containing information about the generated report upload.

    This function generates a small market research report based on provided Factiva and spend reports
    associated with a specific company. It reads the reports from Azure Blob Storage, processes them,
    generates a list of questions, builds an HTML report, and uploads the generated report to Azure Blob Storage.
    """
    container_client_factiva = blob_service_client.get_container_client("factiva")
    container_client_spend_report = blob_service_client.get_container_client(
        "spendcube-aggregated"
    )
    try:
        factiva_report = container_client_factiva.download_blob(factiva_report_name)
    except ResourceNotFoundError:
        return JSONResponse(
            content={
                "response": "The factiva file is not found on Azure",
                "status": "error",
            }
        )
    try:
        spend_report = container_client_spend_report.download_blob(spend_report_name)
    except ResourceNotFoundError:
        return JSONResponse(
            content={
                "response": "The spendcube file is not found on Azure",
                "status": "error",
            }
        )

    with tempfile.NamedTemporaryFile(
        delete=False, prefix="FactivaReport_", suffix=".pdf"
    ) as temp_pdf_file:
        temp_pdf_file.write(io.BytesIO(factiva_report.readall()).getvalue())
        print(f"Temporary file saved at: {temp_pdf_file.name}")
        pdf_path = temp_pdf_file.name

    with tempfile.NamedTemporaryFile(
        delete=False, prefix="SpendReport_", suffix=".xlsx"
    ) as temp_xlsx_file:
        temp_xlsx_file.write(io.BytesIO(spend_report.readall()).getvalue())
        print(f"Temporary file saved at: {temp_xlsx_file.name}")
        csv_path = temp_xlsx_file.name

    questions = generate_small_list_of_questions(company_name, pdf_path, csv_path)

    temp_html_report = tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".html"
    )
    build_report(questions, company_name, temp_html_report.name)
    container_client_result = blob_service_client.get_container_client("result")

    with open(temp_html_report.name, "rb") as data:
        blob_name = (
            f"Market_Research_{company_name}_" + generate_random_string(3) + ".html"
        )
        container_client_result.upload_blob(name=blob_name, data=data)

    return JSONResponse(
        content={
            "response": f"The small market research is uploaded on Azure Storage with blob name: {blob_name}",
            "filename": blob_name,
            "status": "ok",
        }
    )
