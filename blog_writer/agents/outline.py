import json
from typing import List, Tuple, Dict

from langchain_core.messages import SystemMessage, HumanMessage

from blog_writer.agents.base import AgentInterface
from blog_writer.config.logger import logger
from blog_writer.model.search import SearchResult, SearchStringResult
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import wrap_text_with_tag
from blog_writer.utils.stream_token_handler import StreamTokenHandler
from blog_writer.utils.text import extract_json_from_markdown, load_json


class OutlineAgentOutput:
    outline = ""
    
    def __init__(self, answer: str = ""):
        answer = extract_json_from_markdown(answer)
        self.raw_response = answer
        if answer == "":
            return
        answer = extract_json_from_markdown(answer)
        data = load_json(answer)
        self.outline = data["outline"]


class OutlineAgent(AgentInterface):
    @staticmethod
    def render_system_message():
        system_message = SystemMessage(
            content=load_agent_prompt("outline")
        )
        return system_message

    @staticmethod
    def render_human_message(
            subject: str,
            references: SearchResult,
    ):
        content = wrap_text_with_tag(subject, "subject")
        if references is not None:
            content += wrap_text_with_tag(references.get_minified(), "reference")
        logger.info("\033[31m****Outline Agent human message****\n%s\033[0m", content)
        return HumanMessage(content=content)

    def run(
            self,
            topic: str,
            references: SearchResult | SearchStringResult,
    ) -> OutlineAgentOutput:
        human_message = self.render_human_message(
            subject=topic,
            references=references,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]
        content = StreamTokenHandler(self.llm)(messages)
        ai_message = f"{content}\n"
        return OutlineAgentOutput(ai_message)
