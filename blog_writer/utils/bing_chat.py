
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

class BingChatModel:
    @staticmethod
    async def _call_llm(question: str) -> dict:
        bot = None
        response_llm = {}
        try:
            mode = "Bing"
            if mode == "Bing":
                cookies: list[dict] = json.loads(
                    open(
                        f"{ROOT_DIR}/data/bing_cookies.json", encoding="utf-8"
                    ).read()
                )
            else:
                cookies: list[dict] = json.loads(
                    open(
                        f"{ROOT_DIR}/data/copilot_cookies.json",
                        encoding="utf-8",
                    ).read()
                )
            bot = await Chatbot.create(cookies=cookies)
            response = await bot.ask(
                prompt=question,
                conversation_style=ConversationStyle.creative,
                simplify_response=True,
                search_result=True,
            )
            # If you are using non ascii char you need set ensure_ascii=False
            logger.info(json.dumps(response, indent=2, ensure_ascii=False))
            # Raw response
            response_llm = response
        except Exception as error:
            logger.error("Error in calling LLM", error, exc_info=True)
        finally:
            if bot is not None:
                await bot.close()
        return response_llm

    def _generate(self, question: str) -> dict:
        # strim mesage if length > 4000
        if len(question) > 4000:
            question = question[:4000]
            logger.warning("Message is too long, trimming to 4000 characters")
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
    