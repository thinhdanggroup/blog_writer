import json
from typing import List, Tuple, Dict

from langchain.schema import HumanMessage, SystemMessage

from blog_writer.agents.base import AgentInterface
from blog_writer.config.logger import logger
from blog_writer.prompts import load_agent_prompt


class WriterAgentOutput:
    def __init__(self, answer: str = ""):
        self.content = answer


class WriterAgent(AgentInterface):
    def render_system_message(self):
        system_message = SystemMessage(
            content=load_agent_prompt("writer")
        )
        return system_message

    def render_human_message(
            self,
            subject: str,
            references: Dict[str, List[str]],
            previous_content: str,
            current_session: str,
    ):
        content = f"Subject: {subject}\n"

        # reference docs
        content += "Reference documents:\n"
        for doc, msg in references.items():
            list_docs = 'Topic:' + doc + "\n" + '\n'.join(msg)
            content += f"{list_docs}\n"

        # outline
        # outline_content = "Outline :\n"
        # i = 1
        # for o in outline:
        #     outline_content += f"{i}: {o['header']}:{o['short_description']}\n"
        #     i = i + 1
        # content += outline_content

        # previous content
        content += "Previous content of blog from another engineer: " + previous_content + '\n'

        # current session
        content += "Your part that you write: " + current_session + '\n'

        # previous content

        logger.info("\033[31m****Writer Agent human message****\n%s\033[0m", content)
        return HumanMessage(content=content)

    def run(
            self,
            topic: str,
            references: Dict[str, List[str]],
            previous_content: str,
            current_session: str,
    ) -> WriterAgentOutput:
        human_message = self.render_human_message(
            subject=topic,
            references=references,
            previous_content=previous_content,
            current_session=current_session,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        ai_message = f"{self.llm(messages).content}\n"
        return WriterAgentOutput(ai_message)
