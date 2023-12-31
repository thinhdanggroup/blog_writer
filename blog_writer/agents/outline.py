import json
from typing import List, Tuple, Dict

from langchain.schema import HumanMessage, SystemMessage

from blog_writer.agents.base import AgentInterface
from blog_writer.config.logger import logger
from blog_writer.model.search import SearchResult
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import wrap_text_with_tag


class OutlineAgentOutput:
    def __init__(self, answer: str = ""):
        self.raw_response = answer
        if answer == "":
            return
        data = json.loads(answer)
        self.outline = data["outline"]
        self.title = data["title"]


class OutlineAgent(AgentInterface):
    def render_system_message(self):
        system_message = SystemMessage(
            content=load_agent_prompt("outline")
        )
        return system_message

    def render_human_message(
            self,
            subject: str,
            references: SearchResult,
    ):
        content = wrap_text_with_tag(subject, "subject")
        content += wrap_text_with_tag(json.dumps(references, indent=2, cls=ObjectEncoder), "reference")
        logger.info("\033[31m****Outline Agent human message****\n%s\033[0m", content)
        return HumanMessage(content=content)

    def run(
            self,
            topic: str,
            references: SearchResult,
    ) -> OutlineAgentOutput:
        human_message = self.render_human_message(
            subject=topic,
            references=references,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        ai_message = f"{self.llm(messages).content}\n"
        return OutlineAgentOutput(ai_message)
