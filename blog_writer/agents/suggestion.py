import json
from typing import List, Tuple, Dict

from langchain.schema import HumanMessage, SystemMessage

from blog_writer.agents.base import AgentInterface
from blog_writer.config.logger import logger
from blog_writer.model.search import SearchResult
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import wrap_text_with_tag


class SuggestionAgentOutput:
    def __init__(self, answer: str = ""):
        self.content = answer


class SuggestionAgent(AgentInterface):
    def render_system_message(self):
        system_message = SystemMessage(
            content=load_agent_prompt("suggestion")
        )
        return system_message

    def render_human_message(
            self,
            subject: str,
            blog: str,
    ):
        content = wrap_text_with_tag(subject, "blog")
        content += wrap_text_with_tag(blog, "blog")
        logger.info("\033[31m****Suggestion Agent human message****\n%s\033[0m", content)
        return HumanMessage(content=content)

    def run(
            self,
            subject: str,
            blog: str,
    ) -> SuggestionAgentOutput:
        human_message = self.render_human_message(
            subject=subject,
            blog=blog,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        ai_message = f"{self.llm(messages).content}\n"
        return SuggestionAgentOutput(ai_message)
