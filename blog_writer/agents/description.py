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


class DescriptionAgentOutput:
    def __init__(self, answer: str = ""):
        answer = extract_json_from_markdown(answer)
        self.raw_response = answer
        if answer == "":
            return
        print(answer)
        data = load_json(answer)
        print(data)
        
        self.title = data["title"]
        self.description = data["description"]


class DescriptionAgent(AgentInterface):
    @staticmethod
    def render_system_message():
        system_message = SystemMessage(
            content=load_agent_prompt("description")
        )
        return system_message

    @staticmethod
    def render_human_message(
        topic: str,
            outline: str,
    ):
        content = wrap_text_with_tag(topic, "purpose")
        content += wrap_text_with_tag(outline, "outline")
        return HumanMessage(content=content)

    def run(
            self,
            topic: str,
            outline: str,
    ) -> DescriptionAgentOutput:
        human_message = self.render_human_message(
            topic=topic,
            outline=outline,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]
        content = StreamTokenHandler(self.llm)(messages)
        ai_message = f"{content}\n"
        return DescriptionAgentOutput(ai_message)
