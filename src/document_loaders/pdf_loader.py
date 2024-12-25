from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from src.document_loaders.abstract_loader import AbstractLoader


class PdfLoader(AbstractLoader):
    def __init__(self, pdf_paths):
        """
        Initializes a PdfLoader object with specified PDF file paths.

        Args:
        - pdf_paths (list): List of paths to PDF documents.
        """
        self.paths = pdf_paths

    def get_retriever(self):
        return super().get_retriever()

    def _build_index(self):
        pages = self._build_pages()
        return FAISS.from_documents(pages, self.embedder)

    def _build_pages(self):
        pages = []
        for path in self.paths:
            loader = PyPDFLoader(path)
            pages.extend(loader.load_and_split())
        return pages
