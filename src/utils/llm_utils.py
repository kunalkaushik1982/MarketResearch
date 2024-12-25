from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
import json
import os


def create_embedding():
    json_path = os.path.join(os.getcwd(), "credentials", "credentials.json")
    credentials = json.load(open(json_path))

    OPENAI_API_TYPE = credentials.get("OPENAI_API_TYPE")
    OPENAI_API_VERSION = credentials.get("OPENAI_API_VERSION")
    EMBED_BASE_URL = credentials.get("EMBED_BASE_URL")
    EMBED_DEPLOYMENT_NAME = credentials.get("EMBED_DEPLOYMENT_NAME")
    EMBED_API_KEY = credentials.get("EMBED_API_KEY")
    EMBED_MODEL_NAME = credentials.get("EMBED_MODEL_NAME")

    return OpenAIEmbeddings(
        model=EMBED_MODEL_NAME,
        deployment=EMBED_DEPLOYMENT_NAME,
        openai_api_version=OPENAI_API_VERSION,
        openai_api_base=EMBED_BASE_URL,
        openai_api_type=OPENAI_API_TYPE,
        openai_api_key=EMBED_API_KEY,
        chunk_size=1,
        request_timeout=120,
    )


def create_llm():
    json_path = os.path.join(os.getcwd(), "credentials", "credentials.json")
    credentials = json.load(open(json_path))

    BASE_URL = credentials.get("QA_BASE_URL")
    DEPLOYMENT_NAME = credentials.get("QA_DEPLOYMENT_NAME")
    API_KEY = credentials.get("QA_API_KEY")
    OPENAI_API_TYPE = credentials.get("OPENAI_API_TYPE")
    OPENAI_API_VERSION = credentials.get("OPENAI_API_VERSION")

    return AzureChatOpenAI(
        model_name="gpt-35-turbo-16k",
        openai_api_base=BASE_URL,
        openai_api_version=OPENAI_API_VERSION,
        deployment_name=DEPLOYMENT_NAME,
        openai_api_key=API_KEY,
        openai_api_type=OPENAI_API_TYPE,
        temperature=0,
        request_timeout=120,
    )


def create_llm_gpt4():
    json_path = os.path.join(os.getcwd(), "credentials", "credentials.json")
    credentials = json.load(open(json_path))
    BASE_URL = credentials.get("QA_BASE_URL_4")
    DEPLOYMENT_NAME = credentials.get("QA_DEPLOYMENT_NAME_4")
    API_KEY = credentials.get("QA_API_KEY_4")
    OPENAI_API_TYPE = credentials.get("OPENAI_API_TYPE")
    OPENAI_API_VERSION = credentials.get("OPENAI_API_VERSION")

    return AzureChatOpenAI(
        model_name="gpt-4",
        openai_api_base=BASE_URL,
        openai_api_version=OPENAI_API_VERSION,
        deployment_name=DEPLOYMENT_NAME,
        openai_api_key=API_KEY,
        openai_api_type=OPENAI_API_TYPE,
        temperature=0,
        request_timeout=120,
    )
