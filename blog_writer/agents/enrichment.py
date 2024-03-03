import json
from typing import List, Tuple, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from blog_writer.agents.base import AgentInterface
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

from re_edge_gpt import Chatbot
from re_edge_gpt import ConversationStyle


class EnrichmentAgentOutput:
    def __init__(self, answer: dict = None):
        self.content = ""
        if answer is None:
            answer = {}

        if len(answer) == 0:
            return
        self.has_answer = True
        self.content = self._extract_text(answer["text"])
        self.raw_response = answer
        self.suggestions: List[str] = answer.get("suggestions", [])

    @staticmethod
    def _extract_text(text: str) -> str:
        """
        I have input " some text ```md\nsome code \n``` some more text"
        I want to extract "some code" and return it
        Args:
            text:

        Returns:

        """
        code_start = text.find("```")
        if code_start == -1:
            return text
        code_end = text.rfind("```")
        if code_end == -1:
            return text

        return text[code_start + 5:code_end]


class EnrichmentAgent:
    @staticmethod
    def render_system_message() -> str:
        return load_agent_prompt("enrichment")

    def render_human_message(
            self,
            template: str,
            section_topic: str,
            current_content: str,
    ) -> str:
        return template.format(
            purpose=section_topic,
            content=current_content,
        )

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

        # try:
        #     loop = asyncio.get_running_loop()
        #     return loop.run_until_complete(self._call_llm(question))
        # except RuntimeError:
        #     logger.warning("RuntimeError in _generate", exc_info=True)
        return asyncio.run(self._call_llm(question))

    def run(
            self,
            section_topic: str,
            current_content: str,
    ) -> EnrichmentAgentOutput:
        human_message = self.render_human_message(
            template=self.render_system_message(),
            section_topic=section_topic,
            current_content=current_content,
        )

        return EnrichmentAgentOutput(self._generate(human_message))


if __name__ == "__main__":
    q = """
    write a outline for the blog How to
    """
    
    writer_agent = EnrichmentAgent()
    print(writer_agent.run(
        section_topic="Header: Understanding Generation_config \n Your content of this section must be written about Explaining the parameters of generation_config (temperature, top_p, top_k, max_output_tokens) and their impact on the randomness and coherence of generated content. Providing examples and best practices for choosing optimal values.",
        current_content="## Understanding Generation_config\n\nThe generation_config in Gemini AI encompasses a set of parameters that exert a profound influence on the nature of the generated content. These parameters empower users to fine-tune the model's behavior, striking a delicate balance between randomness and coherence.\n\n### Parameters of Generation_config\n\nThe generation_config comprises four primary parameters:\n\n1. **Temperature:** This parameter governs the randomness of the generated text. A higher temperature results in more unpredictable and diverse content, while a lower temperature yields more predictable and coherent text.\n\n2. **Top-p:** This parameter controls the probability distribution over the tokens in the vocabulary. A higher top-p value assigns higher probabilities to the most likely tokens, leading to more fluent and grammatically correct text. Conversely, a lower top-p value broadens the probability distribution, increasing the likelihood of unexpected and creative tokens.\n\n3. **Top-k:** This parameter limits the number of tokens considered during the generation process. A higher top-k value allows for a wider range of tokens to be included, resulting in more diverse content. However, a lower top-k value restricts the token pool, promoting coherence and reducing the risk of repetition.ƒ",
    ))

    # test_data = "I can help you write more detail for this phase. Here is my result in markdown format:\n\n```md\n## Introduction\n\nGemini is a powerful and versatile AI model that can generate text, images, and code. It is trained on a massive dataset of text and code, and it can be used for a variety of tasks, such as:\n\n* **Natural language processing:** Gemini can be used for tasks such as text classification, question answering, and machine translation. For example, you can use Gemini to create a chatbot that can answer questions about your product or service, or to translate your website into different languages.\n* **Image generation:** Gemini can be used to generate realistic images from scratch, or to edit existing images. For example, you can use Gemini to create a logo for your brand, or to change the background of your photo.\n* **Code generation:** Gemini can be used to generate code in a variety of programming languages. For example, you can use Gemini to create a website, an app, or a game.\n\nGemini is a powerful tool that can be used to create amazing things. However, it is important to use it responsibly. The generation_config and safety settings of Gemini can be used to control the quality, diversity, and safety of the generated content.\n\nThe generation_config is a set of parameters that you can adjust to customize the output of Gemini. For example, you can change the length, the temperature, the top-k, and the top-p of the generated text. You can also specify the domain, the language, and the format of the output.\n\nThe safety settings are a set of rules that you can apply to filter out any harmful or inappropriate content from the output of Gemini. For example, you can enable the profanity filter, the toxicity filter, the plagiarism filter, and the personal information filter. You can also define your own custom filters based on your needs and preferences.\n\nIn this blog post, I will show you how to fine-tune the generation_config and safety settings of Gemini for different scenarios and domains. I will also show you some examples of the amazing things that you can create with Gemini.\n```"
    # print(EnrichmentAgentOutput._extract_text(test_data))
