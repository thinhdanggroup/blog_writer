import json
from typing import List, Tuple, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from blog_writer.agents.base import AgentInterface
from blog_writer.config.logger import logger
from blog_writer.model.search import SearchResult
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import wrap_text_with_tag
from blog_writer.utils.stream_token_handler import StreamTokenHandler


class ExampleWriterOutput:
    def __init__(self, answer: str = ""):
        self.content = answer


class ExampleWriter(AgentInterface):
    def render_system_message(self):
        system_message = SystemMessage(
            content=load_agent_prompt("example_writer")
        )
        return system_message

    def render_human_message(
            self,
            content: str,
    ):
        content += "\n Now, give me example for the phase that I provided."
        return HumanMessage(content=content)

    def run(
            self,
            content: str,
    ) -> ExampleWriterOutput:
        human_message = self.render_human_message(
            content=content,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        content = self.call_llm(messages)
        ai_message = f"{content}\n"
        return ExampleWriterOutput(ai_message)
