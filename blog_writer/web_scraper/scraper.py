from typing import List, Optional

import openai
import requests

from blog_writer.config.config import ModelConfig, WebExtractorConfig, WebSearchConfig, load_config
from blog_writer.config.logger import logger
from blog_writer.web_scraper.base import WebScraperInterface
from blog_writer.web_scraper.factory import create_web_extractor, create_web_search
from blog_writer.model.search import Document


class WebScraper(WebScraperInterface):
    def __init__(
            self,
            model_config: ModelConfig,
            web_search_config: WebSearchConfig,
            web_extractor_config: WebExtractorConfig,
    ):
        self._web_searcher = create_web_search(config=web_search_config)
        self._web_extractor = create_web_extractor(
            model_config=model_config,
            extractor_config=web_extractor_config,
        )
        self._max_result = web_search_config.num_results

    def scrape(self, query: str, questions: List[str]) -> List[Document]:
        query += ' -inurl:medium.com'
        hrefs = self._web_searcher.search(query=query)
        ref_sources = []

        asked = "\n".join(questions)
        found = 0
        for href in hrefs:
            try:
                if href.endswith(".pdf"):
                    logger.error("Not support pdf now")
                    continue

                if href.startswith("https://arxiv.org"):
                    logger.error("Not support arxiv.org now")
                    continue

                logger.info("Extracting from %s", href)
                search_result: Optional[Document] = self._web_extractor.extract(url=href, query=asked)
                if search_result is None or len(search_result.answers) == 0:
                    continue

                search_result.href = href
                found += 1
                ref_sources.append(search_result)
                if found >= self._max_result:
                    break
            except KeyboardInterrupt:
                logger.warning("Keyboard interrupt")
                exit(0)
            except requests.exceptions.ConnectionError as e:
                logger.warning("Connection error when extracting from %s error %s", href, e)
            except Exception as e:
                logger.exception("Error when extracting from %s error %s", href, e)

        return ref_sources

if __name__ == "__main__":
    config = load_config()

    wc = WebScraper(config.model_config, config.web_search, config.web_extractor)
    print(wc.scrape("chain of thought llm", ["how to use chain of thought"]))
