from langchain.utilities import SerpAPIWrapper
from langchain.utilities import GoogleSerperAPIWrapper
import json
import os


def create_search():
    json_path = os.path.join(os.getcwd(), "credentials", "credentials.json")
    credentials = json.load(open(json_path))
    SERPAPI_API_KEY = credentials.get("SERPAPI_API_KEY")
    return SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)


def create_search_serper():
    credentials = json.load(open("credentials/credentials.json"))
    SERPER_API_KEY = credentials.get("SERPER_API_KEY")
    return GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)
