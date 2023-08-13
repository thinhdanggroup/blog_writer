from abc import ABC
from typing import Optional

from langchain.callbacks.base import BaseCallbackHandler

from blog_writer.config.config import ModelConfig
from blog_writer.utils.llm import create_chat_model


class AgentInterface(ABC):
    def __init__(
            self,
            model_config: ModelConfig,
            temperature: float = 0,
            stream_callback_manager: BaseCallbackHandler = None,
            max_tokens: Optional[int] = None,
            n: Optional[int] = 1,
            callbacks: Optional[list] = None,
    ):
        self.llm = create_chat_model(
            temperature=temperature,
            stream_callback_manager=stream_callback_manager,
            model_config=model_config,
            max_tokens=max_tokens,
            n=n,
            callbacks=callbacks,
        )
        self.model_config = model_config
