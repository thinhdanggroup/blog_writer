import json
from typing import List, Tuple

from langchain_core.messages import HumanMessage
from langchain_core.prompts import SystemMessagePromptTemplate

from blog_writer.agents.base import AgentInterface
from blog_writer.config.logger import logger
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.stream_token_handler import StreamTokenHandler
from blog_writer.utils.text import extract_json_from_markdown, load_json


class TopicsAgentOutput:
    def __init__(self, answer: str = ""):
        if answer == "":
            self.topics = {}
            return
        if "An unexpected error occurred" in answer:
            raise Exception(
                "You must refresh session in https://chat.tsengineering.io/"
            )
        self.topics = self._parse_answer(answer)

    def _parse_answer(self, answer: str) -> dict:
        answer = extract_json_from_markdown(answer)
        data = load_json(answer)

        topics = {}
        for topic in data["topics"]:
            topics[topic["topic"]] = topic["subtopics"]
        return topics


class TopicAgent(AgentInterface):
    def render_system_message(self, no_topics: int, no_subtopics: int):
        system_template = load_agent_prompt("topics")
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            system_template
        )

        system_message = system_message_prompt.format(
            no_topics=no_topics,
            no_subtopics=no_subtopics,
        )
        return system_message

    def render_human_message(
        self,
        topic: str,
    ):
        content = f"Subject: {topic}"
        logger.info("\033[31m****Outline Agent human message****\n%s\033[0m", content)
        return HumanMessage(content=content)

    def run(
        self,
        subject: str,
        no_topics: int = 3,
        no_subtopics: int = 3,
    ) -> TopicsAgentOutput:
        human_message = self.render_human_message(
            topic=subject,
        )

        messages = [
            self.render_system_message(no_topics=no_topics, no_subtopics=no_subtopics),
            human_message,
        ]

        content = StreamTokenHandler(self.llm)(messages)
        ai_message = f"{content}\n"
        return TopicsAgentOutput(ai_message)


def main():
    data = """
    {
    "topics": [
        {
            "topic": "Creative Coding Projects",
            "subtopics": [
                "What are some unique coding projects that can be completed in a weekend?",
                "How to create interactive art using code?",
                "What are some examples of creative coding projects that have gone viral?",
                "How to use machine learning to generate art?",
                "What are some resources for learning creative coding?",
                "How to create a generative music system using code?",
                "What are some examples of creative coding projects that have been used in advertising?",
                "How to create a interactive story using code?",
                "What are some tools and libraries for creative coding?",
                "How to create a creative coding project for a non-technical audience?"
            ],
            "keywords": "creative coding, coding projects, interactive art, machine learning, generative art, music generation"
        },
        {
            "topic": "Innovative Uses of Emerging Technologies",
            "subtopics": [
                "What are some innovative uses of augmented reality?",
                "How to use blockchain technology to create a secure and transparent system?",
                "What are some examples of innovative uses of artificial intelligence?",
                "How to use the Internet of Things (IoT) to create a smart home?",
                "What are some innovative uses of 3D printing?",
                "How to use virtual reality to create an immersive experience?",
                "What are some examples of innovative uses of natural language processing?",
                "How to use computer vision to create a surveillance system?",
                "What are some innovative uses of robotics?",
                "How to use edge computing to create a real-time analytics system?"
            ],
            "keywords": "emerging technologies, innovation, augmented reality, blockchain, artificial intelligence, IoT, 3D printing, virtual reality"
        },
        {
            "topic": "Cool Tools and Libraries for Developers",
            "subtopics": [
                "What are some cool tools for debugging code?",
                "How to use a code generator to speed up development?",
                "What are some examples of cool libraries for data visualization?",
                "How to use a package manager to manage dependencies?",
                "What are some cool tools for testing code?",
                "How to use a code formatter to improve code readability?",
                "What are some examples of cool libraries for machine learning?",
                "How to use a code linter to improve code quality?",
                "What are some cool tools for collaboration?",
                "How to use a version control system to manage code changes?"
            ],
            "keywords": "developer tools, libraries, debugging, code generation, data visualization, package management, testing, code formatting"
        },
        {
            "topic": "Unique Applications of Machine Learning",
            "subtopics": [
                "What are some unique applications of machine learning in healthcare?",
                "How to use machine learning to predict stock prices?",
                "What are some examples of unique applications of machine learning in finance?",
                "How to use machine learning to create a chatbot?",
                "What are some unique applications of machine learning in education?",
                "How to use machine learning to create a recommendation system?",
                "What are some examples of unique applications of machine learning in marketing?",
                "How to use machine learning to create a predictive maintenance system?",
                "What are some unique applications of machine learning in environmental science?",
                "How to use machine learning to create a sentiment analysis system?"
            ],
            "keywords": "machine learning, applications, healthcare, finance, education, chatbots, recommendation systems, predictive maintenance"
        },
        {
            "topic": "DIY Electronics and Robotics Projects",
            "subtopics": [
                "What are some DIY electronics projects for beginners?",
                "How to create a robot using Arduino?",
                "What are some examples of DIY electronics projects using Raspberry Pi?",
                "How to create a home automation system using DIY electronics?",
                "What are some DIY robotics projects using LEGO Mindstorms?",
                "How to create a DIY drone using Arduino?",
                "What are some examples of DIY electronics projects using ESP32?",
                "How to create a DIY weather station using Arduino?",
                "What are some DIY robotics projects using Python?",
                "How to create a DIY security system using DIY electronics?"
            ],
            "keywords": "DIY electronics, robotics, Arduino, Raspberry Pi, home automation, LEGO Mindstorms, drones, ESP32, weather stations, security systems"
        }
    ]
}
    """

    print(TopicsAgentOutput(data).topics)


if __name__ == "__main__":
    main()
