import asyncio
import json
import logging
import os
from typing import List

import requests
from pydantic import BaseModel

from re_edge_gpt import Chatbot, ConversationStyle
from tenacity import retry, stop_after_attempt, wait_fixed, wait_random, before_log

from blog_writer.config.config import load_config
from blog_writer.config.logger import logger

from blog_writer.config.definitions import ROOT_DIR, HFModel, TSModel

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from hugchat import hugchat
from hugchat.types.message import Conversation
from hugchat.login import Login
from blog_writer.utils.base_chat_model import BaseChatModel
from blog_writer.utils.text import count_tokens


class ResponseMessage(BaseModel):
    content: str = ""


class TSChatModel(BaseChatModel):
    def __init__(self, model_name: str = ""):
        super().__init__()
        self.config = load_config()
        cookie_config = ""
        self.model_name = model_name
        ts_cookie_file = os.environ.get(
            "TS_COOKIE_FILE", ROOT_DIR + "/data/ts_cookies.json"
        )
        if os.path.exists(ts_cookie_file):
            with open(ts_cookie_file, "r") as f:
                cookie_config = f.read()
        cookie_config = json.loads(cookie_config)
        cookie_value = ""
        for cookie in cookie_config["cookies"]:
            name = cookie.get("name", "")
            value = cookie.get("value", "")
            if not name and not value:
                raise ValueError("Cookie name and value must be provided")
            cookie_value += f"{name}={value}; "
        self.cookie_value = cookie_value

    def _call_llm(self, messages: List[BaseMessage], debug=True) -> dict:
        url = "https://chat.tsengineering.io/api/chat/azure"

        msgs = []
        for message in messages:
            if message.type == "system":
                msgs.append(
                    {
                        "role": "user",
                        "content": message.content,
                    }
                )
            else:
                msgs.append(
                    {
                        "role": "system",
                        "content": message.content,
                    }
                )

        payload = {
            "chatSettings": {
                "model": self.model_name,
                "prompt": "You are a friendly, helpful AI assistant.",
                "temperature": 0.5,
                "contextLength": 4096,
                "includeProfileContext": True,
                "includeWorkspaceInstructions": True,
                "embeddingsProvider": "openai",
            },
            "messages": msgs,
            "customModelId": "",
        }

        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,vi;q=0.8",
            "content-type": "text/plain;charset=UTF-8",
            "cookie": self.cookie_value,
            "origin": "https://chat.tsengineering.io",
            "priority": "u=1, i",
            "referer": "https://chat.tsengineering.io/756a4e04-4e3c-472f-bdf0-ee8fbcf32624/chat",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }
        response = requests.request(
            "POST", url, headers=headers, data=json.dumps(payload)
        )

        return {
            "text": response.text,
        }

    def _generate(self, question: str) -> dict:
        # trim message if length > 4000
        # total_tokens = count_tokens(question)
        # if total_tokens > 6000:
        #     question = question[:10000]
        #     logger.warning("Message is too long, trimming to 10000 characters")
        answer = self._call_llm(
            [
                SystemMessage(content="You are a friendly, helpful AI assistant."),
                HumanMessage(content=question),
            ]
        )

        return {
            "text": answer["text"],
        }

    def stream(
        self,
        messages: List[BaseMessage],
    ) -> List[ResponseMessage]:
        answer = self._call_llm(messages)
        return [ResponseMessage(content=answer["text"])]


if __name__ == "__main__":
    chat = TSChatModel(TSModel.GPT_4O.value)
    print(
        chat.stream(
            [HumanMessage(content="hi")],
        )
    )
