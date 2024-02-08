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


class WriteCritiqueAgentOutput:
    def __init__(self, answer: str = ""):
        data = load_json(answer)
        self.success = data.get("success", True)
        self.critique = data.get("critique", "no critique")
        self.reasoning = data.get("reasoning", "no reasoning")


class WriteCritiqueAgent(AgentInterface):
    def render_system_message(self):
        system_message = SystemMessage(
            content=load_agent_prompt("write_critique")
        )
        return system_message

    def render_human_message(
            self,
            subject: str,
            outline: str,
            references: SearchResult,
            previous_content: str,
            current_session: str,
    ):
        content = wrap_text_with_tag(subject, "subject")

        # reference docs
        content += wrap_text_with_tag(json.dumps(references, indent=2, cls=ObjectEncoder), "reference")

        # previous content
        content += wrap_text_with_tag(previous_content, "completed_content")

        # current session
        content += wrap_text_with_tag(current_session, "review_content")

        logger.info("\033[31m****Write Critique Agent human message****\n%s\033[0m", content)
        return HumanMessage(content=content)

    def run(
            self,
            topic: str,
            outline: str,
            references: SearchResult,
            previous_content: str,
            current_session: str,
    ) -> WriteCritiqueAgentOutput:
        human_message = self.render_human_message(
            subject=topic,
            outline=outline,
            references=references,
            previous_content=previous_content,
            current_session=current_session,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        content = StreamTokenHandler(self.llm)(messages)
        ai_message = f"{content}\n"
        return WriteCritiqueAgentOutput(ai_message)
