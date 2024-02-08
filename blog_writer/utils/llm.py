from typing import Optional

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI
from blog_writer.config.config import ModelConfig


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

    if model_config.llm_type == "azure":
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
    else :
        return ChatGoogleGenerativeAI(
            google_api_key=model_config.key,
            model=model_config.deployment,
            temperature=temperature,
            streaming=streaming,
            callbacks=callbacks,
            max_tokens=max_tokens,
            verbose=verbose,
            n=n,
            convert_system_message_to_human=True,
        )
