from datetime import datetime
import json
from typing import List, Tuple, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from blog_writer.agents.base import AgentInterface
from blog_writer.config.config import load_config
from blog_writer.config.definitions import ROOT_DIR
from blog_writer.config.logger import logger
from blog_writer.model.search import SearchResult
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import wrap_text_with_tag
from blog_writer.utils.stream_token_handler import StreamTokenHandler
import asyncio
import json
from pathlib import Path

from re_edge_gpt import Chatbot, ImageGen
from re_edge_gpt import ConversationStyle


class ImageGeneratorAgent(AgentInterface):
    @staticmethod
    def render_system_message():
        system_message = SystemMessage(
            content=load_agent_prompt("image_generator")
        )
        return system_message
    
    @staticmethod
    async def _call_llm(desc: str):
        bot = None
        try:
            cookie = open(f"{ROOT_DIR}/data/bing_cookies.json", "r+").read()
            parsed_cookie = json.loads(cookie)
            for value in parsed_cookie:
                if value["name"] == "_U":
                    auth_cooker = value["value"]
                    break
            
            if auth_cooker is None:
                raise Exception("Cookie not found")
                
            sync_gen = ImageGen(auth_cookie=auth_cooker)
            image_list = sync_gen.get_images(desc)
            name = datetime.now().strftime("%Y%m%d%H%M%S")
            for i, image_url in enumerate(image_list):
                sync_gen.save_images([image_url], f"{ROOT_DIR}/.working_space/images", file_name=f"{name}_{i}")
                print(f"Image saved at {ROOT_DIR}/.working_space/images/{name}_{i}")
        except Exception as error:
            logger.error("Error in calling LLM", error, exc_info=True)
        finally:
            if bot is not None:
                await bot.close()
        return

    def _generate(self, desc: str) -> dict:
        # strim mesage if length > 4000
        if len(desc) > 4000:
            desc = desc[:4000]

        return asyncio.run(self._call_llm(desc))

    def run(
            self,
            desc: str,
    ):
        # generate new content
        messages = [
            self.render_system_message(),
            HumanMessage(content=f"This is the blog description: {desc}"),
            HumanMessage(content=f"Please generate idea to create image for this description.")
        ]
        
        idea = f"Create image about this description:\n{desc}"
        try: 
            idea = StreamTokenHandler(self.llm)(messages,debug=True)
            
        except Exception as e:
            print(f"Error in generating idea: {e}")
        
        self._generate(desc=f"Create image about this description:\n{idea}")


if __name__ == "__main__":
    q = """
    This article is a step-by-step guide to mastering end-to-end testing in NestJS applications using TypeScript. It covers the importance of E2E testing, setting up the testing environment, and writing and running E2E tests. The article also provides unique insights into testing scenarios involving PostgreSQL and Redis databases, including the Cache Aside pattern. Whether you're a beginner or an experienced developer, this article offers valuable knowledge and best practices to ensure the reliability and robustness of your NestJS applications.
    """
    config = load_config()
    writer_agent = ImageGeneratorAgent(
        model_config=config.model_config_hf_chat,
    )
    writer_agent.run(q)
