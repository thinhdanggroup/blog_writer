import json
from typing import Dict, List

from blog_writer.agents.outline import OutlineAgent, OutlineAgentOutput
from blog_writer.agents.suggestion import SuggestionAgent
from blog_writer.agents.topics import TopicAgent, TopicsAgentOutput
from blog_writer.agents.write_critique import WriteCritiqueAgent, WriteCritiqueAgentOutput
from blog_writer.agents.writer import WriterAgent
from blog_writer.config.config import load_config, new_model_config
from blog_writer.config.definitions import ROOT_DIR, MODEL_NAME
from blog_writer.config.logger import logger
from blog_writer.model.search import SearchResult
from blog_writer.store.storage import Storage
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import read_file
from blog_writer.utils.stream_console import StreamConsoleCallbackManager
from blog_writer.utils.text import load_json
from blog_writer.web_scraper import WebScraper
from final_blog import fix_format

TOPIC_FILE = "topics.json"
SEARCH_FILE = "search.json"
OUTLINE_FILE = "outline.json"
BLOG_FILE = "blog.md"
FINAL_BLOG_FILE = "final_blog.md"
SUGGESTION = "suggestion.json"


def generate_topics(topic: str, storage, no_topics: int = 5, no_subtopics: int = 5,
                    debug: bool = False) -> TopicsAgentOutput:
    if debug:
        return TopicsAgentOutput(answer=read_file(f"{ROOT_DIR}/data/example_topics.json"))

    if storage.read(TOPIC_FILE) != "":
        out = TopicsAgentOutput()
        out.topics = load_json(storage.read("topics.json"))
        return out

    stream_callback = StreamConsoleCallbackManager()
    model_config = new_model_config(MODEL_NAME)
    topic_agent = TopicAgent(model_config=model_config, stream_callback_manager=stream_callback, temperature=0.5)

    output = topic_agent.run(topic, no_topics=no_topics, no_subtopics=no_subtopics)
    storage.write(TOPIC_FILE, json.dumps(output.topics))
    return output


def search_from_topics(subject: str, topics: dict, config, storage, debug: bool = False) -> SearchResult:
    web_scarper = WebScraper(config.model_config, config.web_search, config.web_extractor)

    if debug:
        return json.loads(read_file(f"{ROOT_DIR}/data/example_search.json"))

    if storage.read(SEARCH_FILE) != "":
        return json.loads(storage.read(SEARCH_FILE))

    result = SearchResult()
    outline = dict()

    for _, topic in enumerate(topics):
        contents = web_scarper.scrape(f"{topic}", topics[topic])
        if len(contents) == 0:
            continue
        outline[topic] = contents
    result.result = outline
    storage.write(SEARCH_FILE, json.dumps(result, cls=ObjectEncoder))
    return result


def write_outline(subject: str, references: SearchResult, storage,
                  debug: bool = False) -> OutlineAgentOutput:
    if debug:
        return read_file(f"{ROOT_DIR}/data/example_writer.txt")

    if storage.read(OUTLINE_FILE) != "":
        data = storage.read(OUTLINE_FILE)
        return OutlineAgentOutput(answer=data)

    stream_callback = StreamConsoleCallbackManager()
    model_config = new_model_config(MODEL_NAME)
    writer_agent = OutlineAgent(model_config=model_config, stream_callback_manager=stream_callback, temperature=0.5)

    output = writer_agent.run(subject, references)
    storage.write(OUTLINE_FILE, output.raw_response)
    return output


def critique(subject: str, outline: str, completed_part: str, current_part: str, references: SearchResult,
             debug: bool = False) -> WriteCritiqueAgentOutput:
    if debug:
        return read_file(f"{ROOT_DIR}/data/example_writer.txt")

    stream_callback = StreamConsoleCallbackManager()
    model_config = new_model_config(MODEL_NAME)
    writer_agent = WriteCritiqueAgent(model_config=model_config, stream_callback_manager=stream_callback,
                                      temperature=0.2)

    output = writer_agent.run(subject, outline, references, completed_part, current_part)
    return output


def write_blog(outline_blog, outline_output, references: SearchResult, storage, subject,
               use_critique: bool = False) -> str:
    blog_content = storage.read(BLOG_FILE)
    if blog_content != "":
        return blog_content
    write_config = new_model_config(MODEL_NAME)
    writer_agent = WriterAgent(model_config=write_config, stream_callback_manager=StreamConsoleCallbackManager(),
                               temperature=0.5)
    cur_blog = ""
    i = 1

    max_retry = 1
    for o in outline_output.outline:
        i = 0
        suggestions = ""
        last_content = ""
        while i <= max_retry:
            out_content = writer_agent.run(subject, references, cur_blog,
                                           f"Header: {o['header']} \n Your content must be written about {o['short_description']}",
                                           suggestions)
            last_content = out_content.content
            i += 1

            if not use_critique or i == max_retry:
                break

            critiq = critique(subject, outline_blog, cur_blog, out_content.content, references)
            # if critiq.success:
            #     break
            suggestions = critiq.critique

        cur_blog += last_content + "\n\n"
        i += 1

    storage.write(BLOG_FILE, cur_blog)
    return cur_blog


def generate(subject, load_from, skip_all: bool = True):
    config = load_config()
    subject = subject.strip()
    storage = Storage(subject, load_from_workspace=load_from)

    output = generate_topics(subject, storage, 5, 10, False)
    if not skip_all:
        continue_ok = input("Search: Press Enter to continue...")
        if continue_ok != 'y':
            logger.info(storage.workspace)
            return

    references = search_from_topics(subject, output.topics, config, storage, False)
    outline_output = write_outline(subject, references, storage, False)

    if not skip_all:
        continue_ok = input("Outline: Press Enter to continue...")
        if continue_ok != 'y':
            logger.info(storage.workspace)
            return

    outline_blog = json.dumps(outline_output.outline)
    blog_content = write_blog(outline_blog, outline_output, references, storage, subject)

    if storage.read(SUGGESTION) != "":
        logger.info("Suggestion already generated")
    else:
        write_config = new_model_config(MODEL_NAME)
        suggest_agent = SuggestionAgent(model_config=write_config,
                                        stream_callback_manager=StreamConsoleCallbackManager(),
                                        temperature=0.1)
        output = suggest_agent.run(subject, blog_content)
        logger.info(output.content)
        storage.write(SUGGESTION, output.content)

    storage.write(FINAL_BLOG_FILE, fix_format(storage))

    # critiq = critique(subject, outline_blog, "", blog_content, SearchResult(), False)
    # if critiq.success:
    #     logger.info("Blog is ready to publish")
    # else:
    #     logger.info("Blog is not ready to publish")
    #     logger.info(critiq.critique)


if __name__ == "__main__":
    problem = read_file("input.txt")
    subject = f'Write a blog about\n\"\"\"{problem}\n\"\"\"'
    load_from = ""
    generate(subject, load_from)
