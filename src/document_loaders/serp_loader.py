from langchain.vectorstores import FAISS
from langchain.document_loaders import SeleniumURLLoader
from src.utils.serp_utils import create_search
from src.document_loaders.abstract_loader import AbstractLoader


class SerpLoader(AbstractLoader):
    search = create_search()

    def __init__(self, serp_prompts):
        """
        Initializes a SerpLoader object with specified search engine prompts.

        Args:
        - serp_prompts (list): List of prompts for search engine queries.
        """
        self.serp_prompts = serp_prompts

    def get_retriever(self):
        return super().get_retriever()

    def _build_index(self):
        pages = self._build_pages()
        return FAISS.from_documents(pages, self.embedder)

    def _build_pages(self):
        urls = self._get_urls()
        return SeleniumURLLoader(urls=self._filter_non_pdf_urls(urls)).load_and_split()

    def _get_urls(self):
        url_list = []
        for prompt in self.serp_prompts:
            results = self.search.results(prompt)
            url_list.extend([item["link"] for item in results["organic_results"]])
        return url_list

    @staticmethod
    def _filter_non_pdf_urls(url_list):
        return list(filter(lambda url: not url.endswith(".pdf"), url_list))
