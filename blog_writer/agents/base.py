import logging
from abc import ABC
from typing import Dict, Optional, List

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from tenacity import retry, stop_after_attempt, wait_fixed, wait_random, before_log

from blog_writer.config.config import ModelConfig
from blog_writer.config.logger import logger
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.file import wrap_text_with_tag
from blog_writer.utils.llm import create_chat_model
from blog_writer.utils.stream_token_handler import StreamTokenHandler
from langchain_core.messages import SystemMessage, HumanMessage


class AgentInterface(ABC):
    def __init__(
        self,
        model_config: ModelConfig,
        fallback_model_config: Optional[ModelConfig] = None,
        temperature: float = 0,
        stream_callback_manager: BaseCallbackHandler = None,
        max_tokens: Optional[int] = None,
        n: Optional[int] = 1,
        callbacks: Optional[list] = None,
        debug: bool = False,
        retry_count: int = 3,
    ):
        self.llm = create_chat_model(
            temperature=temperature,
            stream_callback_manager=stream_callback_manager,
            model_config=model_config,
            max_tokens=max_tokens,
            n=n,
            callbacks=callbacks,
        )
        if fallback_model_config is not None:
            self.llm_fallback = create_chat_model(
                temperature=temperature,
                stream_callback_manager=stream_callback_manager,
                model_config=fallback_model_config,
                max_tokens=max_tokens,
                n=n,
                callbacks=callbacks,
            )
        self.model_config = model_config
        self.debug = debug

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(10) + wait_random(0, 2),
        before=before_log(logger, logging.INFO),
    )
    def _call_main_llm(self, messages: List[BaseMessage]) -> str:
        return StreamTokenHandler(self.llm)(messages=messages, debug=self.debug)

    def _call_fallback_llm(self, messages: List[BaseMessage]) -> str:
        return StreamTokenHandler(self.llm_fallback)(
            messages=messages, debug=self.debug
        )

    def call_llm(self, messages: List[BaseMessage]) -> str:
        try:
            return self._call_main_llm(messages)
        except Exception as e:
            logger.error(
                f"Error calling main model. Use fallback model name {self.model_config.llm_type}"
            )
            return self._call_fallback_llm(messages)


class BaseAgent(AgentInterface):
    def __init__(
        self,
        model_config: ModelConfig,
        system_prompt: str,
        fallback_model_config: Optional[ModelConfig] = None,
        temperature: float = 0,
        stream_callback_manager: BaseCallbackHandler = None,
        max_tokens: Optional[int] = None,
        n: Optional[int] = 1,
        callbacks: Optional[list] = None,
        debug: bool = False,
        retry_count: int = 3,
    ):
        super().__init__(
            model_config=model_config,
            fallback_model_config=fallback_model_config,
            temperature=temperature,
            stream_callback_manager=stream_callback_manager,
            max_tokens=max_tokens,
            n=n,
            callbacks=callbacks,
            debug=debug,
            retry_count=retry_count,
        )

        self.system_prompt = system_prompt

    def render_system_message(self):
        system_message = SystemMessage(content=load_agent_prompt(self.system_prompt))
        return system_message

    def render_human_message(
        self,
        params: Dict[str, str],
    ):
        content = "\n".join([wrap_text_with_tag(v, k) for k, v in params.items()])
        return HumanMessage(content=content)

    def run(
        self,
        params: Dict[str, str] = {},
    ) -> str:
        human_message = self.render_human_message(
            params=params,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        content = self.call_llm(messages)
        ai_message = f"{content}\n"
        return ai_message
