# Market Research

## Requisites

- Download python 3.10

## Getting started

- Create a python environment and download requirements

```
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

- Organize Your Files: 

Put Factiva Reports in a "factiva" folder.
Put Spending Reports in a "SpendReport" folder.
Put credentials in a "credentials" folder

- To grasp the logic behind the code structure, refer to files prefixed with 'abstract' where comprehensive docstrings are provided.

## Generating a market research report

To generate a report, execute the following command in the terminal:

```
python main.py --company {{whatever company}}
```

Replace {{whatever company}} with the specific company name you want to generate the report for.

The result of this command will be an HTML report named "{{whatever company}}.html", containing the insights and analysis for the specified company.



## Generating a market research report through API 

To generate a report using the API, follow these steps:

Execute the following command in the terminal to initialize the API:

```
bash entrypoint.sh
```

This command will start the API. 

Once the API is running, you can make requests to it to generate reports automatically. 







