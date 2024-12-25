from abc import ABC, abstractmethod
from typing import List
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.prompts import PromptTemplate
from src.utils.custom_prompt import combine_prompt_template_test
import json
import re
from src.document_loaders.abstract_loader import AbstractLoader
from src.utils.llm_utils import create_llm, create_llm_gpt4


class AbstractQuestion(ABC):
    @abstractmethod
    def write(self, html_file):
        print(type(self).__name__)


class QuestionWithLLM(AbstractQuestion):
    """
    Parent class for questions leveraging Language Model-based answers (LLM).
    This class serves as a template for various question types requiring LLM responses.
    """

    def __init__(
        self,
        title: str,
        prompt: str,
        loader: AbstractLoader,
        llm_model: str,
        backup_loaders: List[AbstractLoader] = [],
    ):
        """
        Initializes a QuestionWithLLM object.

        Args:
        - title (str): The title of the question that will be displayed in the report.
        - prompt (str): The gpt prompt for the question.
        - loader (AbstractLoader): The loader object for data retrieval.
        - llm_model (str): The type of Language Model for question answering (gpt3.5 or gpt4).
        - backup_loaders (List[AbstractLoader], optional): Backup loaders if
        primary pdf loader fails. Defaults to an empty list.
        """
        self.prompt = prompt
        self.title = title
        self.loader = loader
        self.llm_model = llm_model
        self.backup_loaders = backup_loaders
        self._qa = None
        self._answer = None
        self._answer_json = None
        self._raw_question = None
        self._raw_answer = None
        self._sources = None

    def write(self, html_file):
        """
        Writes the question's title, answer, and sources into an HTML file.

        Args:
        - html_file: File object for writing HTML content.
        """
        if not (self._check_answer()):
            self._switch_retriever_and_reset()

        html_file.write(
            '<h2 style="color: #003883;font-size: 130%;">' + self.title + "</h2>\n"
        )
        html_file.write(
            '<h4 style="color: #d30473;font-size: 110%;">'
            + self.answer_json["answer"]
            + "</h4>\n"
        )
        html_file.write('<h4 style="color: #223349;font-size: 110%;">')
        if len(self.sources) == 0:
            print("no sources")
            html_file.write(
                "<a> <li>" + "An error occured: no sources available" + "</li> </a>"
            )

        else:
            for source in self.sources[0].split(" ; "):
                html_file.write("<a href=" + source + "> <li>" + source + "</li> </a>")
        html_file.write("</h4>\n")

    @property
    def qa(self):
        """
        Retrieves the QA model for answering the question.

        Returns:
        - QA model: The Question Answering model.
        """
        if self._qa is None:
            self._qa = self._build_qa_model()
        return self._qa

    @property
    def answer(self):
        """
        Retrieves the answer in string format.

        Returns:
        - str: The answer in string format.
        """
        if self._answer is None:
            self._answer = json.dumps(self.qa(self.prompt))
        return self._answer

    @property
    def answer_json(self):
        """
        Retrieves the answer in JSON format.

        Returns:
        - dict: The answer in JSON format.
        """
        if self._answer_json is None:
            self._answer_json = json.loads(self.answer)
        return self._answer_json

    def _check_answer(self):
        """
        Checks whether the question-answering model found a relevant response.

        Returns:
        - bool: True if there is a relevant response, False otherwise.
        """
        keywords_pattern = r"(not\smention|no\sinformation|no\smention|not\sprovid|not\scontain|i\sdon't\sknow)"

        answer_text = self.answer_json["answer"].lower()

        if re.search(keywords_pattern, answer_text):
            return False

        sources = self.answer_json["sources"]

        if isinstance(sources, str) and re.search(
            r"^(none|n/a|none\sprovided|)$", sources.lower()
        ):
            return False

        return True

    def _reset_answer(self):
        """
        Resets the answer-related attributes to None.
        """
        self._qa = None
        self._answer = None
        self._answer_json = None
        self._raw_question = None
        self._raw_answer = None
        self._sources = None

    def _switch_retriever_and_reset(self):
        """
        Switches to a backup loader and resets answer-related attributes.
        """
        if len(self.backup_loaders) > 0:
            self.loader = self.backup_loaders[0]
            self.backup_loaders.pop()
            self._reset_answer()

    @property
    def sources(self):
        """
        Retrieves the sources of the answer.

        Returns:
        - list: List of sources.
        """
        if self._sources is None:
            if isinstance(self.answer_json["sources"], str):
                self._sources = [self.answer_json["sources"]]
            else:
                self._sources = self.answer_json["sources"]
        return self._sources

    def _build_qa_model(self):
        """
        Builds the Question Answering with sources model.

        Returns:
        - QA model: The Question Answering model.
        """
        return RetrievalQAWithSourcesChain.from_chain_type(
            self._select_llm(),
            retriever=self.loader.get_retriever(),
            chain_type="stuff",
            chain_type_kwargs={
                "prompt": PromptTemplate(
                    template=combine_prompt_template_test,
                    input_variables=["summaries", "question"],
                ),
            },
        )

    def _select_llm(self):
        """
        Selects the appropriate Language Model for answering.

        Returns:
        - LLM model: The Language Model for answering.
        """
        if self.llm_model == "gpt4":
            return create_llm_gpt4()
        else:
            return create_llm()
