import json
from typing import List, Optional

from tenacity import retry, retry_if_exception_type, stop_after_attempt
from blog_writer.agents.base import BaseAgent
from blog_writer.agents.query_generator import QueryGeneratorAgent
from blog_writer.cache.cache_service import CacheService
from blog_writer.config.logger import logger
from blog_writer.config.config import Config, load_config
from blog_writer.config.definitions import SnapshotFileType
from blog_writer.crawler.crawl_service import CrawlingService
from blog_writer.model.search import Answer, Document, SearchResult, SearchStringResult
from blog_writer.prompts import load_agent_prompt
from blog_writer.store.storage import Storage
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import read_file
from blog_writer.utils.llm import count_tokens, create_chat_model
from blog_writer.utils.stream_console import StreamConsoleCallbackManager
from blog_writer.utils.stream_token_handler import StreamTokenHandler
from blog_writer.utils.text import load_json
from langchain_core.messages import SystemMessage, HumanMessage
import threading


class CrawlExtractor:
    def __init__(self, config: Config, storage: Storage, model_config=None):
        self.config = config
        self.storage = storage
        self.model_config = (
            config.model_config_ts_chat if model_config is None else model_config
        )

        self.extract_answer = BaseAgent(
            model_config=self.model_config,
            system_prompt="extract",
        )
        self.extract_code = BaseAgent(
            model_config=self.model_config,
            system_prompt="extract_code",
        )

    def search_from_topics(self, subject: str, topics: dict) -> SearchResult:
        if (
            self.storage.read(SnapshotFileType.SEARCH_FILE) != ""
            and self.config.web_extractor.use_cache
        ):
            logger.info("Load search result from file")
            result = SearchResult()
            result.load_from_json(self.storage.read(SnapshotFileType.SEARCH_FILE))
            return result

        urls = read_file(SnapshotFileType.REFERENCE_INPUT)

        crawl_data = CrawlingService.crawl(urls=urls)
        references = SearchStringResult(result=crawl_data)
        total_token = count_tokens(crawl_data)
        logger.info(f"References {urls} with total token {total_token}")
        if total_token > 80000:
            logger.info(f"References is too long, skip")
            exit(0)

        result = SearchResult()
        outline = dict()

        logger.info(f"Search from topics {topics}")

        def process_topic(topic):
            logger.info(f"With topic {topic} and references {references}")
            contents = self.scrape(
                subject=subject, content=references, questions=topics[topic]
            )

            if len(contents) > 0:
                outline[topic] = contents

        threads = []
        for _, topic in enumerate(topics):
            thread = threading.Thread(target=process_topic, args=(topic,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join(timeout=120)

        # Check if any threads are still alive after the timeout
        for thread in threads:
            if thread.is_alive():
                logger.info(f"Thread {thread.name} timed out")

        result.result = outline
        self.storage.write(
            SnapshotFileType.SEARCH_FILE, json.dumps(result, cls=ObjectEncoder)
        )
        return result

    def scrape(
        self, subject: str, content: SearchStringResult, questions: List[str]
    ) -> List[Document]:
        ref_sources = []

        asked = "\n".join(questions)

        search_result: Optional[Document] = self._summarize_text(
            text=content.get_minified(), question=asked, subject=subject
        )
        if search_result is None or len(search_result.answers) == 0:
            return ref_sources

        ref_sources.append(search_result)
        return ref_sources

    @retry(
        retry=retry_if_exception_type(json.JSONDecodeError),
        stop=stop_after_attempt(3),
    )
    def _summarize_text(
        self, subject: str, text: str, question: str
    ) -> Optional[Document]:
        if not text:
            return None

        text = text.strip()
        if len(text) < 100:
            logger.info("Text is too short")
            return None

        if not self.config.web_extractor.with_summary:
            logger.info("Skip summary")
            return None

        model = create_chat_model(
            temperature=self.config.web_extractor.temperature,
            model_config=self.model_config,
            stream_callback_manager=StreamConsoleCallbackManager(),
        )

        total_tokens = count_tokens(text)
        if total_tokens > 64000:
            raise ValueError("The text is too long to summarize")

        # messages = [
        #     self._get_system_prompt(),
        #     self._create_message(text=text, question=question),
        # ]

        # data = StreamTokenHandler(model)(messages, debug=True)
        data = self.extract_answer.run(
            params={
                "web_site_content": text,
                "questions": question,
            }
        )
        result = load_json(data, True)
        text_result = Document()
        for question in result.get("questions", []):
            if not question.get("has_answer", False):
                continue
            q = question.get("question", "")

            if "answer" not in question:
                continue
            text_result.answers.append(Answer(question=q, answer=question["answer"]))

        code = self.extract_code.run(
            params={
                "purpose": subject,
                "reference_documents": text,
            }
        )
        
        text_result.code = code

        return text_result


if __name__ == "__main__":
    config = load_config()
    config.web_extractor.use_cache = False

    storage = Storage(
        subject="Guide to AI Memory Building",
        load_from_workspace="250127133254_guide-to-ai-memory-building-",
    )
    crawl_service = CrawlExtractor(
        config=config,
        storage=storage,
        model_config=config.model_config_ts_chat,
    )
    subject = "Guide to AI Memory Building"

    topics = json.loads(
        read_file(
            ".working_space/250127133254_guide-to-ai-memory-building-/topics.json"
        )
    )
    references = crawl_service.search_from_topics(
        subject=subject,
        topics=topics,
    )
