import abc
from typing import List, Optional

from blog_writer.model.search import Document


class WebSearcherInterface:
    @abc.abstractmethod
    def search(self, query: str) -> List[str]:
        pass


class WebExtractorInterface:
    @abc.abstractmethod
    def extract(self, url: str, query: str) -> Optional[Document]:
        pass


class WebScraperInterface:
    @abc.abstractmethod
    def scrape(self, query: str, questions: List[str]) -> List[Document]:
        pass
