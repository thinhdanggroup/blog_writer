import json
from typing import List, Tuple, Dict

from blog_writer.utils.text import load_json
from langchain_core.messages import HumanMessage, SystemMessage

from blog_writer.agents.base import AgentInterface
from blog_writer.config.logger import logger
from blog_writer.model.search import SearchResult
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import wrap_text_with_tag
from blog_writer.utils.stream_token_handler import StreamTokenHandler


class ExtractRelevantSearchOutput:
    def __init__(self, answer: str = ""):
        self.raw_response = answer
        if answer == "":
            return
        
        try:
            data = load_json(answer,True)
            self.content = data["retrieved_content"]
        except Exception as e:
            self.content = answer


class ExtractRelevantSearchAgent(AgentInterface):
    def render_system_message(self):
        system_message = SystemMessage(
            content=load_agent_prompt("extract_relevant_search")
        )
        return system_message

    def render_human_message(
            self,
            purpose: str,
            references: SearchResult,
            need_to_retrieve: str,
    ):
        content = wrap_text_with_tag(purpose, "purpose")

        # reference docs
        content += wrap_text_with_tag(json.dumps(references, indent=2, cls=ObjectEncoder), "reference")

        # previous content
        content += wrap_text_with_tag(need_to_retrieve, "need_to_retrieve")
        
        return HumanMessage(content=content)

    def run(
            self,
            purpose: str,
            references: SearchResult,
            need_to_retrieve: str,
    ) -> ExtractRelevantSearchOutput:
        human_message = self.render_human_message(
            purpose=purpose,
            references=references,
            need_to_retrieve=need_to_retrieve,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        content = StreamTokenHandler(self.llm)(messages)
        ai_message = f"{content}\n"
        return ExtractRelevantSearchOutput(ai_message)
