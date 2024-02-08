import sys
from typing import Any, Optional, List
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult
from tenacity import RetryCallState

from blog_writer.config.logger import logger


class StreamTokenHandler:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.output = ""

    @staticmethod
    def _parse_message(messages: List[BaseMessage]) -> str:
        output = ""
        for message in messages:
            if message.content:
                output += message.content
        return output

    def __call__(self, messages: List[BaseMessage]) -> str:
        logger.info("\033[31m****StreamTokenHandler****\n%s\033[0m", self._parse_message(messages))

        for chunk in self.llm.stream(messages):
            content = chunk.content
            self.output += content

        logger.info("\033[31m****StreamTokenHandler output****\n%s\033[0m", self.output)
        return self.output
