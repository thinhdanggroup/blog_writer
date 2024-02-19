import json
from typing import List, Tuple, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from blog_writer.agents.base import AgentInterface
from blog_writer.config.config import new_model_config
from blog_writer.config.definitions import MODEL_NAME
from blog_writer.config.logger import logger
from blog_writer.model.search import SearchResult
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import wrap_text_with_tag
from blog_writer.utils.stream_console import StreamConsoleCallbackManager
from blog_writer.utils.stream_token_handler import StreamTokenHandler


class QueryGeneratorOutput:
    def __init__(self, answer: str = ""):
        self.content = answer


class QueryGeneratorAgent(AgentInterface):
    @staticmethod
    def render_system_message():
        system_message = SystemMessage(
            content=load_agent_prompt("query_generator")
        )
        return system_message

    @staticmethod
    def render_human_message(
            topic: str,
            sub_topic: str,
    ):
        content = wrap_text_with_tag(topic, "topic")
        content += wrap_text_with_tag(sub_topic, "sub_topic")
        return HumanMessage(content=content)

    def run(
            self,
            topic: str,
            sub_topic: str,
    ) -> QueryGeneratorOutput:
        human_message = self.render_human_message(
            topic=topic,
            sub_topic=sub_topic,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        content = StreamTokenHandler(self.llm)(messages)
        ai_message = f"{content}\n"
        return QueryGeneratorOutput(ai_message)


if __name__ == "__main__":
    topic_in = """
    Help me write a blog post about comparing Serverless vs. Containers: Compare and contrast serverless and containers in terms of:
- Architecture: How do they work? What are the main components and features?
- Deployment: How do they run and scale? What are the requirements and limitations?
- Performance: How do they handle load and latency? What are the trade-offs and best practices?
- Cost: How do they charge and optimize? What are the factors and scenarios that affect the pricing?
- Security: How do they protect and isolate? What are the risks and mitigations?
- Use cases: What are the typical and ideal scenarios for each? What are some examples and success stories?
    """
    write_config = new_model_config(MODEL_NAME)
    agent = QueryGeneratorAgent(
        model_config=write_config,
        stream_callback_manager=StreamConsoleCallbackManager(),
        temperature=0.5,
    )
    output = agent.run(
        topic=topic_in,
        sub_topic="Architecture"
    )
    print(output.content)
