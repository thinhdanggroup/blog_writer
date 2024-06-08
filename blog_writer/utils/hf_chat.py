import asyncio
import json
from typing import List
from pydantic import BaseModel

from re_edge_gpt import Chatbot, ConversationStyle

from blog_writer.config.config import load_config
from blog_writer.config.logger import logger

from blog_writer.config.definitions import ROOT_DIR, HFModel

from langchain_core.messages import BaseMessage, HumanMessage
from hugchat import hugchat
from hugchat.types.message import Conversation
from hugchat.login import Login
from blog_writer.utils.base_chat_model import BaseChatModel
from blog_writer.utils.text import count_tokens


class ResponseMessage(BaseModel):
    content: str = ""


COOKIES_PATH = f"{ROOT_DIR}/data/hf_cookies/"


class HFChatModel(BaseChatModel):
    def __init__(self, model_name: str = ""):
        super().__init__()
        config = load_config()
        sign = Login(
            config.model_config_hf_chat.username, config.model_config_hf_chat.key
        )
        cookies = sign.login(cookie_dir_path=COOKIES_PATH, save_cookies=True)
        chatbot = hugchat.ChatBot(
            cookies=cookies.get_dict()
        )  # or cookie_path="usercookies/<email>.json"
        models = chatbot.get_available_llm_models()

        model_idx = -1

        idx = 0
        for m in models:
            if m.name == model_name:
                model_idx = idx
                break
            idx += 1

        if model_idx == -1:
            raise Exception(f"Model {model_name} not found")

        chatbot.switch_llm(model_idx)

        self.chatbot = chatbot

    async def _call_llm(self, question: str) -> dict:
        conv = self.chatbot.new_conversation(
            switch_to=True
        )  # switch to the new conversation
        conv_id = conv.id

        response_llm = ""

        for resp in self.chatbot.query(question, stream=True):
            if resp is None:
                break

            if "token" in resp:
                response_llm += resp["token"]

        return {
            "text": response_llm,
        }

    def _generate(self, question: str) -> dict:
        # strim mesage if length > 4000
        total_tokens = count_tokens(question)
        if total_tokens > 6000:
            question = question[:10000]
            logger.warning("Message is too long, trimming to 10000 characters")
        return asyncio.run(self._call_llm(question))

    def stream(
        self,
        messages: List[BaseMessage],
    ) -> List[ResponseMessage]:
        human_message = ""
        for message in messages:
            human_message += message.content + "\n"

        answer = self._generate(human_message)
        return [ResponseMessage(content=answer["text"])]


if __name__ == "__main__":
    chat = HFChatModel(HFModel.LLAMA3.value)
    print(
        chat.stream(
            [HumanMessage(content="write python code to solve sudoku")],
        )
    )
