import asyncio
import json
import os
from datetime import datetime
from typing import Optional
from langchain_core.messages import HumanMessage, SystemMessage
from re_edge_gpt import ImageGen

from blog_writer.agents.base import AgentInterface
from blog_writer.config.config import ModelConfig, load_config
from blog_writer.config.definitions import ROOT_DIR
from blog_writer.config.logger import logger
from blog_writer.prompts import load_agent_prompt
from blog_writer.store.storage import Storage
from blog_writer.utils.stream_token_handler import StreamTokenHandler


class ImageGeneratorAgent(AgentInterface):

    def __init__(
        self,
        model_config: ModelConfig,
        fallback_model_config: Optional[ModelConfig] = None,
        temperature: float = 0,
        stream_callback_manager=None,
        max_tokens: Optional[int] = None,
        n: Optional[int] = 1,
        callbacks: Optional[list] = None,
        debug: bool = False,
        retry_count: int = 3,
        generate_image: bool = True,
        storage: Optional[Storage] = None,
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
        self.generate_image = generate_image
        self.storage = storage

    @staticmethod
    def render_system_message():
        system_message = SystemMessage(content=load_agent_prompt("image_generator"))
        return system_message

    @staticmethod
    async def _call_llm(desc: str, working_dir: str):
        bot = None
        try:
            cookie = open(f"{ROOT_DIR}/data/bing_cookies.json", "r+").read()
            parsed_cookie = json.loads(cookie)
            for value in parsed_cookie["cookies"]:
                if value["name"] == "_U":
                    auth_cooker = value["value"]
                    break

            if auth_cooker is None:
                raise Exception("Cookie not found")

            folder_name = f"{ROOT_DIR}/.working_space/{working_dir}/images"
            try:
                os.makedirs(folder_name)
            except Exception as e:
                logger.warn("folder is existed")

            sync_gen = ImageGen(auth_cookie=auth_cooker)
            image_list = sync_gen.get_images(desc)
            name = datetime.now().strftime("%Y%m%d%H%M%S")

            for i, image_url in enumerate(image_list):
                sync_gen.save_images([image_url], folder_name, file_name=f"{name}_{i}")
                logger.info(f"Image saved at {folder_name}/{name}_{i}")
        except Exception as error:
            logger.error("Error in calling LLM", error, exc_info=True)
        finally:
            if bot is not None:
                await bot.close()
        return

    def _generate(self, desc: str, working_dir: str = "") -> dict:
        # strim mesage if length > 4000
        if len(desc) > 4000:
            desc = desc[:4000]

        return asyncio.run(self._call_llm(desc, working_dir))

    def run(
        self,
        desc: str,
        working_dir: str = "",
    ):
        # generate new content
        messages = [
            self.render_system_message(),
            HumanMessage(content=f"This is the blog description: {desc}"),
            HumanMessage(
                content=f"Please generate idea to create image for this description."
            ),
        ]

        idea = f"Create image about this description:\n{desc}"
        try:
            idea = StreamTokenHandler(self.llm)(messages, debug=True)

        except Exception as e:
            logger.error(f"Error in generating idea: {e}")

        if self.generate_image:
            self._generate(
                working_dir=working_dir,
                desc=f"Create image about this description:\n{idea}",
            )
        else:
            logger.info(f"""Idea: {idea}""")
            if self.storage is not None:
                self.storage.write("image_idea.txt", idea)


if __name__ == "__main__":
    q = """
    This article is a step-by-step guide to mastering end-to-end testing in NestJS applications using TypeScript. It covers the importance of E2E testing, setting up the testing environment, and writing and running E2E tests. The article also provides unique insights into testing scenarios involving PostgreSQL and Redis databases, including the Cache Aside pattern. Whether you're a beginner or an experienced developer, this article offers valuable knowledge and best practices to ensure the reliability and robustness of your NestJS applications.
    """
    config = load_config()
    writer_agent = ImageGeneratorAgent(
        model_config=config.model_config_ollama,
    )
    writer_agent.run(q)
