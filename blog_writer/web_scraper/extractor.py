import requests
from bs4 import BeautifulSoup
from langchain.schema import HumanMessage

from blog_writer.config.config import ModelConfig, WebExtractorConfig
from blog_writer.utils.llm import create_chat_model

from .base import WebExtractorInterface


class WebExtractor(WebExtractorInterface):
    def __init__(self, extractor_config: WebExtractorConfig, model_config: ModelConfig):
        self._extractor_config = extractor_config
        self._model_config = model_config

    def extract(self, url: str, query: str) -> str:
        page_source = requests.get(url=url).content
        soup = BeautifulSoup(page_source, "html.parser")

        for script in soup(["script", "style"]):
            script.extract()

        text = self._get_text(soup=soup)

        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        return self._summarize_text(text=text, question=query)

    def _get_text(self, soup: BeautifulSoup):
        text = ""
        tags = ["h1", "h2", "h3", "h4", "h5", "p"]
        for element in soup.find_all(tags):  # Find all the <p> elements
            text += element.text + "\n\n"
        return text

    def _summarize_text(self, text: str, question: str) -> str:
        if not text:
            return "Error: No text to summarize"

        if not self._extractor_config.with_summary:
            return text

        model = create_chat_model(
            temperature=self._extractor_config.temperature,
            model_config=self._model_config,
            max_tokens=1000,
        )

        return model([self._create_message(text=text, question=question)]).content

    def _create_message(self, text: str, question: str) -> HumanMessage:
        return HumanMessage(
            content=f'"""{text}""" Using the above text, answer the following'
            f' questions: "{question}" -- if the questions cannot be answered using the text.'
            "You return <status>fail<status> if the text is not relevant to questions."
            "Include all factual information, numbers, stats etc if available. Write detail step-by-step answer if possible."
            "If questions about how to implement something, write a step-by-step guide and code if possible."
        )
