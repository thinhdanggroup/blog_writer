import json
from typing import Optional

import requests
from bs4 import BeautifulSoup
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import Html2TextTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.messages import SystemMessage, HumanMessage

from blog_writer.config.config import ModelConfig, WebExtractorConfig
from blog_writer.utils.llm import create_chat_model

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
        loader = AsyncHtmlLoader(urls)
        docs = loader.load()
        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        return docs_transformed[0].page_content

    def extract(self, url: str, query: str) -> Optional[Document]:
        text = self.get_content(url=url)
        # Grab the first 1000 tokens of the site
        # splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        #     chunk_size=30000, chunk_overlap=0
        # )
        # splits = splitter.split_documents(text)
        doc = self._summarize_text(text=text, question=query)
        if doc is None:
            return None
        doc.url = url
        return doc

    def _get_text(self, soup: BeautifulSoup):
        text = ""
        tags = ["h1", "h2", "h3", "h4", "h5", "p"]
        for element in soup.find_all(tags):  # Find all the <p> elements
            text += element.text + "\n\n"
        return text

    def _summarize_text(self, text: str, question: str) -> Optional[Document]:
        if not text:
            return None

        if not self._extractor_config.with_summary:
            return None

        model = create_chat_model(
            temperature=self._extractor_config.temperature,
            model_config=self._model_config,
            stream_callback_manager=StreamConsoleCallbackManager()
        )

        messages = [self._get_system_prompt(), self._create_message(text=text, question=question)]

        data = StreamTokenHandler(model)(messages, debug=False)
        result = load_json(data)
        text_result = Document()
        for question in result.get("questions", []):
            if not question.get("has_answer", False):
                continue
            q = question.get("question", "")

            if "answer" not in question:
                continue
            text_result.answers.append(
                Answer(question=q, answer=question["answer"])
            )
        return text_result

    @staticmethod
    def _get_system_prompt() -> SystemMessage:
        return SystemMessage(
            content=load_agent_prompt("extract")
        )

    @staticmethod
    def _create_message(text: str, question: str) -> HumanMessage:
        msg = "<web_site_content>"
        msg += text
        msg += "</web_site_content>"

        msg += "<questions>"
        msg += question
        msg += "</questions>"

        return HumanMessage(
            content=msg
        )
