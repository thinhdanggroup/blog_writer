import abc
from typing import List


class WebSearcherInterface:
    @abc.abstractmethod
    def search(self, query: str) -> List[str]:
        pass


class WebExtractorInterface:
    @abc.abstractmethod
    def extract(self, url: str, query: str) -> str:
        pass


class WebScraperInterface:
    @abc.abstractmethod
    def scrape(self, query: str, questions: List[str]) -> List[str]:
        pass
