from typing import List

from duckduckgo_search import DDGS

from blog_writer.config.config import WebSearchConfig

from .base import WebSearcherInterface


class DuckDuckGoSearch(WebSearcherInterface):
    def __init__(self, cfg: WebSearchConfig):
        self._ddgs = DDGS()
        self._num_results = cfg.num_results

    def _get_exclude_sites(self) -> str:
        return " -site:medium.com"

    def search(self, query: str) -> List[str]:
        search_results: List[str] = []
        if not query:
            return search_results

        results = self._ddgs.text(query)
        if not results:
            return search_results

        total_added = 0
        for j in results:
            search_results.append(j["href"])
            total_added += 1
            if total_added >= self._num_results * 2:
                break

        return search_results
