import json
from typing import List, Tuple

from langchain_core.messages import HumanMessage
from langchain_core.prompts import SystemMessagePromptTemplate

from blog_writer.agents.base import AgentInterface
from blog_writer.config.logger import logger
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.stream_token_handler import StreamTokenHandler
from blog_writer.utils.text import extract_json_from_markdown, load_json


class TopicsAgentOutput:
    def __init__(self, answer: str = ""):
        if answer == "":
            self.topics = {}
            return
        self.topics = self._parse_answer(answer)

    def _parse_answer(self, answer: str) -> dict:
        answer = extract_json_from_markdown(answer)
        data = load_json(answer)

        topics = {}
        for topic in data['topics']:
            topics[topic['topic']] = topic['subtopics']
        return topics


class TopicAgent(AgentInterface):
    def render_system_message(self,
                              no_topics: int,
                              no_subtopics: int):
        system_template = load_agent_prompt("topics")
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            system_template
        )

        system_message = system_message_prompt.format(
            no_topics=no_topics,
            no_subtopics=no_subtopics,
        )
        return system_message

    def render_human_message(
            self,
            topic: str,
    ):
        content = f"Subject: {topic}"
        logger.info("\033[31m****Outline Agent human message****\n%s\033[0m", content)
        return HumanMessage(content=content)

    def run(
            self,
            subject: str,
            no_topics: int = 3,
            no_subtopics: int = 3,
    ) -> TopicsAgentOutput:
        human_message = self.render_human_message(
            topic=subject,
        )

        messages = [
            self.render_system_message(
                no_topics=no_topics,
                no_subtopics=no_subtopics),
            human_message,
        ]

        content = StreamTokenHandler(self.llm)(messages)
        ai_message = f"{content}\n"
        return TopicsAgentOutput(ai_message)
