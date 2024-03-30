import json
from typing import List, Tuple

from langchain_core.messages import HumanMessage
from langchain_core.prompts import SystemMessagePromptTemplate

from blog_writer.agents.base import AgentInterface
from blog_writer.config.logger import logger
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.stream_token_handler import StreamTokenHandler
from blog_writer.utils.text import extract_json_from_markdown, load_json
from blog_writer.utils.file import wrap_text_with_tag
from langchain_core.messages import SystemMessage, HumanMessage

class EnrichTopicOutput:
    def __init__(self, answer: str = ""):
        if "Generating answers for you" in answer:
            answer_splitted = answer.split("Generating answers for you")
            answer = answer_splitted[0] 
        self.answer = answer


class EnrichTopic(AgentInterface):
    def render_system_message(self):
        system_message = SystemMessage(
            content=load_agent_prompt("enrich_topic")
        )
        return system_message

    def render_human_message(
            self,
            topic: str,
    ):
        return HumanMessage(content=topic)

    def run(
            self,
            subject: str,
    ) -> EnrichTopicOutput:
        human_message = self.render_human_message(
            topic=subject,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        content = StreamTokenHandler(self.llm)(messages)
        return EnrichTopicOutput(content)
