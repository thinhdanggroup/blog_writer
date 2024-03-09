from typing import Optional

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI
from blog_writer.config.config import ModelConfig
from langchain_openai import ChatOpenAI

from blog_writer.config.definitions import LLMType
from blog_writer.utils.bing_chat import BingChatModel
import tiktoken

def create_chat_model(
        temperature: float,
        model_config: ModelConfig,
        stream_callback_manager: BaseCallbackHandler = None,
        verbose: bool = True,
        max_tokens: Optional[int] = None,
        n: int = 1,
        callbacks: Optional[list] = None,
) -> BaseChatModel | BingChatModel:
    streaming = stream_callback_manager is not None
    if callbacks is None:
        callbacks = []

    if stream_callback_manager:
        callbacks.append(stream_callback_manager)

    if model_config.llm_type == LLMType.AZURE:
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
    elif model_config.llm_type == LLMType.OPEN_ROUTER:
        print("Open Router", model_config.deployment, model_config.key, model_config.base)
        return ChatOpenAI(
            openai_api_base=model_config.base,
            openai_api_key=model_config.key,
            model_name=model_config.deployment,
        )
    elif model_config.llm_type == LLMType.BING_CHAT:
        return BingChatModel()
    else:
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
            max_output_tokens=2000,
        )

def count_tokens(tokens: str) -> int:
    enc = tiktoken.encoding_for_model("gpt-4")
    total = len(enc.encode(tokens))
    return total