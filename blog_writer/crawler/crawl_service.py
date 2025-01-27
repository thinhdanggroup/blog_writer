import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from blog_writer.config.logger import logger
from blog_writer.utils.llm import count_tokens
from blog_writer.cache.cache_service import global_cache_service


class CrawlingService:

    @staticmethod
    def crawl(urls: str) -> str:
        result = asyncio.run(CrawlingService.acrawl(urls))
        return result

    def get_list_url(self, urls: str) -> list:
        list_url = urls.split("\n")

        formatted_list = []
        for url in list_url:
            url = url.strip()

            if not url:
                continue

            formatted_list.append(url)
        return formatted_list

    async def acrawl(urls: str) -> str:
        crawl_res = []

        list_url = urls.split("\n")

        for url in list_url:
            if not url:
                continue

            if not url.strip():
                continue
            
            if global_cache_service.get(url):
                logger.info(f"Get url={url} from cache")
                crawl_res.append(global_cache_service.get(url))
                continue
            
            res = await CrawlingService.crawl_url(url=url)
            global_cache_service.put(key=url, value=res)
            crawl_res.append(res)

        return "\n".join(crawl_res)

    @staticmethod
    async def crawl_url(url: str) -> str:
        md_generator = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.4, threshold_type="fixed")
        )
        browser_conf = BrowserConfig(headless=True)  # or False to see the browser
        run_conf = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS, markdown_generator=md_generator
        )
        async with AsyncWebCrawler(config=browser_conf) as crawler:
            result = await crawler.arun(url=url, config=run_conf)

        total_token = count_tokens(result.markdown)
        logger.info(f"Total token for {url}: {total_token}")

        return result.markdown


if __name__ == "__main__":
    print(CrawlingService.crawl("https://www.google.com"))
