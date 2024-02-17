import json
from typing import List, Tuple, Dict

from langchain_core.messages import SystemMessage, HumanMessage

from blog_writer.agents.base import AgentInterface
from blog_writer.config.logger import logger
from blog_writer.model.search import SearchResult
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import wrap_text_with_tag
from blog_writer.utils.stream_token_handler import StreamTokenHandler
from blog_writer.utils.text import extract_json_from_markdown, load_json


class ReviewAgentOutput:
    def __init__(self, answer: str = ""):
        self.review_msg = answer


class ReviewAgent(AgentInterface):
    @staticmethod
    def render_system_message():
        system_message = SystemMessage(
            content=load_agent_prompt("reviewer")
        )
        return system_message

    @staticmethod
    def render_human_message(
            section: str,
            section_content: str
    ):
        content = wrap_text_with_tag(section, "section")
        content += wrap_text_with_tag(section_content, "section_content")
        return HumanMessage(content=content)

    def run(
            self,
            section: str,
            section_content: str,
    ) -> ReviewAgentOutput:
        human_message = self.render_human_message(
            section=section,
            section_content=section_content,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]
        content = StreamTokenHandler(self.llm)(messages)
        ai_message = f"{content}\n"
        return ReviewAgentOutput(ai_message)
