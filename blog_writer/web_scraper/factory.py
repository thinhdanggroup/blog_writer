from blog_writer.config.config import ModelConfig, WebExtractorConfig, WebSearchConfig

from .base import WebExtractorInterface, WebSearcherInterface
from .ddg_search import DuckDuckGoSearch
from .extractor import WebExtractor
from .google_search import GoogleSearch


def create_web_search(config: WebSearchConfig) -> WebSearcherInterface:
    if config.search_engine == "google":
        return GoogleSearch(config)

    return DuckDuckGoSearch(config)


def create_web_extractor(
    extractor_config: WebExtractorConfig, model_config: ModelConfig
) -> WebExtractorInterface:
    return WebExtractor(extractor_config=extractor_config, model_config=model_config)
