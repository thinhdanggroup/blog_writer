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


class TitleGeneratorOutput:
    def __init__(self, answer: str = ""):
        data = load_json(answer)
        self.description = data.get("description", "no_description")


class TitleGenerator(AgentInterface):
    def render_system_message(self):
        system_message = SystemMessage(
            content=load_agent_prompt("title_generator")
        )
        return system_message

    def render_human_message(
            self,
            subject: str,
    ):
        content = wrap_text_with_tag(subject, "subject")
        return HumanMessage(content=content)

    def run(
            self,
            topic: str,
    ) -> TitleGeneratorOutput:
        human_message = self.render_human_message(
            subject=topic,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        content = StreamTokenHandler(self.llm)(messages)
        ai_message = f"{content}\n"
        return TitleGeneratorOutput(ai_message)
