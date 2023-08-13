from typing import Optional

from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.chat_models.base import BaseChatModel

from blog_writer.config.config import ModelConfig
from blog_writer.config.logger import logger


def create_chat_model(
    temperature: float,
    model_config: ModelConfig,
    stream_callback_manager: BaseCallbackHandler = None,
    verbose: bool = True,
    max_tokens: Optional[int] = None,
    n: int = 1,
    callbacks: Optional[list] = None,
) -> BaseChatModel:
    streaming = stream_callback_manager is not None
    if callbacks is None:
        callbacks = []

    if stream_callback_manager:
        callbacks.append(stream_callback_manager)

    return AzureChatOpenAI(
        openai_api_version=model_config.version,
        openai_api_base=model_config.base,
        openai_api_key=model_config.key,
        deployment_name=model_config.deployment,
        temperature=temperature,
        streaming=streaming,
        callbacks=callbacks,
        max_tokens=max_tokens,
        verbose=verbose,
        n=n,
    )