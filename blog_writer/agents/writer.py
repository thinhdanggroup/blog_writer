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


class WriterAgentOutput:
    def __init__(self, answer: str = ""):
        self.content = answer


class WriterAgent(AgentInterface):
    def render_system_message(self):
        system_message = SystemMessage(
            content=load_agent_prompt("writer")
        )
        return system_message

    def render_human_message(
            self,
            subject: str,
            references: SearchResult,
            previous_content: str,
            current_session: str,
            suggestions: str,
    ):
        content = wrap_text_with_tag(subject, "subject")

        # reference docs
        content += wrap_text_with_tag(json.dumps(references, indent=2, cls=ObjectEncoder), "reference")

        # previous content
        content += wrap_text_with_tag(previous_content, "previous_content")

        # current session
        content += wrap_text_with_tag(current_session, "title_and_content")

        content += wrap_text_with_tag(suggestions, "suggestions")

        logger.info("\033[31m****Writer Agent human message****\n%s\033[0m", content)
        return HumanMessage(content=content)

    def run(
            self,
            topic: str,
            references: SearchResult,
            previous_content: str,
            current_session: str,
            suggestions: str,
    ) -> WriterAgentOutput:
        human_message = self.render_human_message(
            subject=topic,
            references=references,
            previous_content=previous_content,
            current_session=current_session,
            suggestions=suggestions,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        content = StreamTokenHandler(self.llm)(messages)
        ai_message = f"{content}\n"
        return WriterAgentOutput(ai_message)
