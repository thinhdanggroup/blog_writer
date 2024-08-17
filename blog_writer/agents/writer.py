import json
from typing import List, Tuple, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from blog_writer.agents.base import AgentInterface
from blog_writer.config.logger import logger
from blog_writer.model.search import SearchResult
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import wrap_text_with_tag
from blog_writer.utils.llm import count_tokens
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
            previous_content: str,
            current_session: str,
            suggestions: str,
            references: SearchResult = None,
            retrieved_data: str = None,
    ):
        content = wrap_text_with_tag(subject, "subject")

        # reference docs
        if references and references.strip() != "":
            content += wrap_text_with_tag(references.get_minified(), "reference")
        
        if retrieved_data and retrieved_data.strip() != "":
            content += wrap_text_with_tag(retrieved_data, "reference")

        # previous content
        total_previous_content_tokens = count_tokens(previous_content)
        if total_previous_content_tokens > 2000:
            # last 3000 characters
            compress_previous_content = "...previous content is hide a part  because it is too long .../n" + previous_content[-3000:]
            content += wrap_text_with_tag(compress_previous_content, "previous_content")

        # current session
        content += wrap_text_with_tag(current_session, "title_and_content")

        if suggestions and suggestions.strip() != "":
            content += wrap_text_with_tag(suggestions, "suggestions")

        logger.info("\033[31m****Writer Agent human message****\n%s\033[0m", content)
        return HumanMessage(content=content)

    def run(
            self,
            topic: str,
            previous_content: str,
            current_session: str,
            suggestions: str,
            references: SearchResult = None,
            retrieved_data: str = None,
    ) -> WriterAgentOutput:
        human_message = self.render_human_message(
            subject=topic,
            references=references,
            previous_content=previous_content,
            current_session=current_session,
            suggestions=suggestions,
            retrieved_data=retrieved_data,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        content = self.call_llm(messages)
        ai_message = f"{content}\n"
        return WriterAgentOutput(ai_message)
