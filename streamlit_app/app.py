import json
from typing import Dict, List

from blog_writer.agents.outline import OutlineAgent, OutlineAgentOutput
from blog_writer.agents.topics import TopicAgent, TopicsAgentOutput
from blog_writer.agents.writer import WriterAgent
from blog_writer.config.config import load_config, new_model_config
from blog_writer.config.definitions import ROOT_DIR
from blog_writer.config.logger import logger
from blog_writer.store.storage import Storage
from blog_writer.utils.file import read_file
from blog_writer.utils.stream_console import StreamConsoleCallbackManager
from blog_writer.web_scraper import WebScraper

TOPIC_FILE = "topics.json"
SEARCH_FILE = "search.json"
OUTLINE_FILE = "outline.json"
BLOG_FILE = "blog.md"


def generate_topics(topic: str, storage, no_topics: int = 5, no_subtopics: int = 5,
                    debug: bool = False) -> TopicsAgentOutput:
    if debug:
        return TopicsAgentOutput(answer=read_file(f"{ROOT_DIR}/data/example_topics.json"))

    if storage.read(TOPIC_FILE) != "":
        out = TopicsAgentOutput()
        out.topics = json.loads(storage.read("topics.json"))
        return out

    stream_callback = StreamConsoleCallbackManager()
    model_config = new_model_config("gpt4-8k")
    topic_agent = TopicAgent(model_config=model_config, stream_callback_manager=stream_callback)

    output = topic_agent.run(topic, no_topics=no_topics, no_subtopics=no_subtopics)
    storage.write(TOPIC_FILE, json.dumps(output.topics))
    return output


def search_from_topics(subject: str, topics: dict, config, storage, debug: bool = False) -> dict:
    web_scarper = WebScraper(config.model_config, config.web_search, config.web_extractor)

    if debug:
        return json.loads(read_file(f"{ROOT_DIR}/data/example_search.json"))

    if storage.read(SEARCH_FILE) != "":
        return json.loads(storage.read(SEARCH_FILE))

    outline = {}

    for _, topic in enumerate(topics):
        contents = web_scarper.scrape(f"{subject} {topic}", topics[topic])
        outline[topic] = contents

    storage.write(SEARCH_FILE, json.dumps(outline))
    return outline


def write_outline(subject: str, references: Dict[str, List[str]], storage,
                  debug: bool = False) -> OutlineAgentOutput:
    if debug:
        return read_file(f"{ROOT_DIR}/data/example_writer.txt")

    if storage.read(OUTLINE_FILE) != "":
        data = storage.read(OUTLINE_FILE)
        return OutlineAgentOutput(answer=data)

    stream_callback = StreamConsoleCallbackManager()
    model_config = new_model_config("gpt4-8k")
    writer_agent = OutlineAgent(model_config=model_config, stream_callback_manager=stream_callback)

    output = writer_agent.run(subject, references)
    storage.write(OUTLINE_FILE, output.raw_response)
    return output


def main():
    config = load_config()

    subject = """
    This blog is about prompt engineering, which is a field of generative AI that focuses on designing and improving prompts for AI models. A prompt is a way of communicating with an AI model, such as asking a question, giving a command, or providing an example. Prompt engineering aims to create effective and efficient prompts that can elicit the desired outputs from the AI models. The blog covers the main aspects and steps of prompt engineering, such as how to design, evaluate, and apply prompts to different domains and use cases. The blog also introduces some tools and platforms that support prompt engineering, such as ChatGPT and Copy.ai. The blog is intended for anyone who is interested in learning more about prompt engineering and how to use it in their own projects.
    """
    load_from = "230813163440_this_blog_is_about_p"
    storage = Storage(subject, load_from_workspace=load_from)

    output = generate_topics(subject, storage, 4, 5, False)
    references = search_from_topics(subject, output.topics, config, storage, False)
    outline_output = write_outline(subject, references, storage, False)

    continue_ok = input("Press Enter to continue...")
    if continue_ok != 'y':
        logger.info(storage.workspace)
        return

    write_config = new_model_config("gpt4-32k")
    writer_agent = WriterAgent(model_config=write_config, stream_callback_manager=StreamConsoleCallbackManager())
    cur_blog = ""
    i = 1
    for o in outline_output.outline:
        out_content = writer_agent.run(subject, references, cur_blog,
                                       f"Header: {o['header']} \n Your content must be written about {o['short_description']}")
        cur_blog += f"Part {i}: {o['header']}\n"
        cur_blog += out_content.content + "\n\n"
        i += 1

    storage.write(BLOG_FILE, cur_blog)


if __name__ == "__main__":
    main()
