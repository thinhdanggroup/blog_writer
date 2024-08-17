from blog_writer.config.config import load_config
from blog_writer.web_scraper import WebScraper


def test_scrape():
    config = load_config()
    config.web_search.num_results = 2
    scraper = WebScraper(config.model_config_ollama, config.web_search, config.web_extractor)
    data = scraper.scrape("pytest in python", ["Give me example pytest?", "What is the best practices pytest?"])
    assert len(data) > 0
