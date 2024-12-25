from abc import ABC, abstractmethod
from typing import List
from langchain.schema import Document
from src.utils.llm_utils import create_embedding


class AbstractLoader(ABC):
    embedder = create_embedding()
    _retriever = None

    def get_retriever(self):
        """
        Retrieval:
        Builds a retriever that will be used in the Question Answering model
        in order to find relevant splits of document relative to each type of question

        Returns:
        - Retriever object: The retriever object.
        """
        if self._retriever is None:
            index = self._build_index()
            self._retriever = index.as_retriever()
        return self._retriever

    @abstractmethod
    def _build_index(self):
        """
        Storage:
        Builds an index of pages using FAISS vector database by OpenAI based
        on loaded textual data (from PDF or search results).

        Returns:
        - FAISS index: The index of pages.
        """
        pass

    @abstractmethod
    def _build_pages(self) -> List[Document]:
        """
        Document loading and splitting:
        Loads and splits pages from native PDF documents or google search results.

        Returns:
        - Pages: The loaded and split pages.
        """
        pass
