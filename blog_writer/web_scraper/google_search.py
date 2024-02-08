import os

from langchain import GoogleSearchAPIWrapper
from langchain_core.tools import Tool

from blog_writer.config.config import WebSearchConfig

from .base import WebSearcherInterface


class GoogleSearch(WebSearcherInterface):
    def __init__(self, cfg: WebSearchConfig):
        self._num_results = cfg.num_results
        self._search_api = GoogleSearchAPIWrapper(
            google_api_key=cfg.google_api_key,
            google_cse_id=cfg.google_cse_id,
        )

    def _top_results(self, query):
        return self._search_api.results(query, self._num_results)

    def search(self, query: str) -> list:
        google_search_tool = Tool(
            name="Google Search Snippets",
            description="Search Google for recent results",
            func=self._top_results,
        )
        google_search_results = google_search_tool.run(query)
        urls = [r["link"] for r in google_search_results if "link" in r]
        return urls


if __name__ == "__main__":
    google_search_engine = GoogleSearch(
        WebSearchConfig(
            {
                "search_engine": "google",
                "num_results": 10,
                "google_api_key": os.getenv("GOOGLE_API_KEY"),
                "google_cse_id": os.getenv("GOOGLE_CSE_ID"),
            }
        )
    )

    results = google_search_engine.search("pip install fail")
    print(results)
