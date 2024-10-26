import json
from json.decoder import JSONDecodeError
from typing import Optional, Type

from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests
from bs4 import BeautifulSoup
from langchain_core.messages import SystemMessage, HumanMessage
from tenacity import retry, stop_after_attempt, retry_if_exception_type

from blog_writer.config.config import ModelConfig, WebExtractorConfig
from blog_writer.utils.llm import count_tokens, create_chat_model
from langchain_community.document_loaders.async_html import AsyncHtmlLoader
from langchain_community.document_transformers.html2text import Html2TextTransformer

from .base import WebExtractorInterface
from ..model.search import Document, Answer
from ..prompts import load_agent_prompt
from ..utils.file import read_file
from ..utils.stream_console import StreamConsoleCallbackManager
from ..utils.stream_token_handler import StreamTokenHandler
from ..utils.text import extract_json_from_markdown, load_json


class WebExtractor(WebExtractorInterface):
    def __init__(self, extractor_config: WebExtractorConfig, model_config: ModelConfig):
        self._extractor_config = extractor_config
        self._model_config = model_config

    def get_content(self, url) -> Optional[str]:
        urls = [url]
        # loader = AsyncHtmlLoader(urls, verify_ssl=False)
        loader = AsyncHtmlLoader(urls)
        docs = loader.load()
        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        if not docs_transformed or len(docs_transformed) == 0:
            return None
        return docs_transformed[0].page_content

    def extract(self, url: str, query: str) -> Optional[Document]:
        text = self.get_content(url=url)
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=8000,
            chunk_overlap=400,
            length_function=len,
            is_separator_regex=False,
        )

        if text is None:
            return None

        texts = text_splitter.create_documents([text])

        summary_docs = Document(url=url, answers=[])

        for data in texts:
            doc = self._summarize_text(text=data.page_content, question=query)
            if doc is None:
                return None

            summary_docs.answers.extend(doc.answers)
        return summary_docs

    def _get_text(self, soup: BeautifulSoup):
        text = ""
        tags = ["h1", "h2", "h3", "h4", "h5", "p"]
        for element in soup.find_all(tags):  # Find all the <p> elements
            text += element.text + "\n\n"
        return text

    @retry(
        retry=retry_if_exception_type(JSONDecodeError),
        stop=stop_after_attempt(3),
    )
    def _summarize_text(self, text: str, question: str) -> Optional[Document]:
        if not text:
            return None

        text = text.strip()
        if len(text) < 100:
            return None

        if not self._extractor_config.with_summary:
            return None

        model = create_chat_model(
            temperature=self._extractor_config.temperature,
            model_config=self._model_config,
            stream_callback_manager=StreamConsoleCallbackManager(),
        )

        total_tokens = count_tokens(text)
        if total_tokens > 32000:
            raise ValueError("The text is too long to summarize")

        messages = [
            self._get_system_prompt(),
            self._create_message(text=text, question=question),
        ]

        data = StreamTokenHandler(model)(messages, debug=True)
        result = load_json(data, True)
        text_result = Document()
        for question in result.get("questions", []):
            if not question.get("has_answer", False):
                continue
            q = question.get("question", "")

            if "answer" not in question:
                continue
            text_result.answers.append(Answer(question=q, answer=question["answer"]))
        return text_result

    @staticmethod
    def _get_system_prompt() -> SystemMessage:
        return SystemMessage(content=load_agent_prompt("extract"))

    @staticmethod
    def _create_message(text: str, question: str) -> HumanMessage:
        msg = "<web_site_content>"
        msg += text
        msg += "</web_site_content>"

        msg += "<questions>"
        msg += question
        msg += "</questions>"

        return HumanMessage(content=msg)
