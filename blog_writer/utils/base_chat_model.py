
from abc import ABC, abstractmethod
import asyncio
import json
from typing import List
from pydantic import BaseModel

from re_edge_gpt import Chatbot, ConversationStyle

from blog_writer.config.logger import logger

from blog_writer.config.definitions import ROOT_DIR

from langchain_core.messages import BaseMessage

class ResponseMessage(BaseModel):
    content: str = ""

class BaseChatModel(ABC):
    @staticmethod
    @abstractmethod
    async def _call_llm(question: str) -> dict:
        raise NotImplementedError("_call_llm method is not implemented")

    @abstractmethod
    def _generate(self, question: str) -> dict:
        raise NotImplementedError("generate method is not implemented")

    @abstractmethod
    def stream(
            self,
            messages: List[BaseMessage],
    ) -> List[ResponseMessage]:
        raise NotImplementedError("stream method is not implemented")