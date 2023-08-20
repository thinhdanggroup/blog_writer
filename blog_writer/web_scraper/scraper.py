from typing import List, Dict, Optional

import openai
import requests

from blog_writer.config.config import ModelConfig, WebExtractorConfig, WebSearchConfig

from blog_writer.config.logger import logger
from .base import WebScraperInterface
from .factory import create_web_extractor, create_web_search
from ..model.search import Document
from ..utils.file import wrap_text_with_tag


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

    def scrape(self, query: str, questions: List[str]) -> List[Document]:
        query += ' -inurl:medium.com'
        hrefs = self._web_searcher.search(query=query)
        ref_sources = []

        asked = "\n".join(questions)
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
                ref_sources.append(search_result)
            except KeyboardInterrupt:
                logger.warning("Keyboard interrupt")
                exit(0)
            except requests.exceptions.ConnectionError:
                logger.warning("Connection error when extracting from %s", href)
            except openai.error.InvalidRequestError as e:
                logger.error("Error when extracting from %s", href)
            except Exception as e:
                logger.exception("Error when extracting from %s %s", href, e)

        return ref_sources
