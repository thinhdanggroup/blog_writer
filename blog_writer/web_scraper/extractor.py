import json
from typing import Optional

import requests
from bs4 import BeautifulSoup
from langchain.schema import HumanMessage, SystemMessage

from blog_writer.config.config import ModelConfig, WebExtractorConfig
from blog_writer.utils.llm import create_chat_model

from .base import WebExtractorInterface
from ..model.search import Document, Answer
from ..prompts import load_agent_prompt
from ..utils.file import read_file
from ..utils.stream_console import StreamConsoleCallbackManager

from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import Html2TextTransformer


class WebExtractor(WebExtractorInterface):
    def __init__(self, extractor_config: WebExtractorConfig, model_config: ModelConfig):
        self._extractor_config = extractor_config
        self._model_config = model_config

    # def get_content(self, url: str) -> Optional[str]:
    #     page_source = requests.get(url=url).content
    #     soup = BeautifulSoup(page_source, "html.parser")
    #
    #     for script in soup(["script", "style"]):
    #         script.extract()
    #
    #     text = self._get_text(soup=soup)
    #
    #     lines = (line.strip() for line in text.splitlines())
    #     chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    #     text = "\n".join(chunk for chunk in chunks if chunk)
    #     return text

    def get_content(self, url) -> Optional[str]:
        urls = [url]
        loader = AsyncHtmlLoader(urls)
        docs = loader.load()
        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        return docs_transformed[0].page_content

    def extract(self, url: str, query: str) -> Optional[Document]:
        text = self.get_content(url=url)
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
            max_tokens=2000,
            stream_callback_manager=StreamConsoleCallbackManager()
        )

        data = model([self._get_system_prompt(), self._create_message(text=text, question=question)]).content
        result = json.loads(data)
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
