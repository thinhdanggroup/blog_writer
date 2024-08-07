import json

from pydantic_core import from_json
from blog_writer.agents.description import DescriptionAgent
from blog_writer.agents.enrich_topic import EnrichTopic

from blog_writer.agents.enrichment import EnrichmentAgent
from blog_writer.agents.example_writer import ExampleWriter
from blog_writer.agents.extract_relevant_search import ExtractRelevantSearchAgent
from blog_writer.agents.image_generator import ImageGeneratorAgent
from blog_writer.agents.outline import OutlineAgent, OutlineAgentOutput
from blog_writer.agents.query_generator import QueryGeneratorAgent
from blog_writer.agents.reviewer import ReviewAgent
from blog_writer.agents.suggestion import SuggestionAgent
from blog_writer.agents.topics import TopicAgent, TopicsAgentOutput
from blog_writer.agents.write_critique import (
    WriteCritiqueAgent,
    WriteCritiqueAgentOutput,
)
from blog_writer.agents.writer import WriterAgent
from blog_writer.config.config import Config, load_config, new_model_config
from blog_writer.config.definitions import (
    MODEL_NAME_GEMINI_PRO_15,
    ROOT_DIR,
    MODEL_NAME,
    LLMType,
    OllamaModel,
    OpenRouterModel,
)
from blog_writer.config.logger import logger
from blog_writer.model.data import OutlineModel, StepTracker
from blog_writer.model.search import SearchResult
from blog_writer.store.storage import Storage
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import read_file
from blog_writer.utils.stream_console import StreamConsoleCallbackManager
from blog_writer.utils.text import load_json
from blog_writer.web_scraper import WebScraper
from blog_writer.core.final_blog import fix_format

TOPIC_FILE = "topics.json"
SEARCH_FILE = "search.json"
OUTLINE_FILE = "outline.json"
BLOG_V1_FILE = "blog_v1.md"
BLOG_V2_FILE = "blog_v2.md"
BLOG_FILE = "blog.md"
STEP_TRACKER = "step_tracker.json"
SUBJECT = "subject.md"
REVIEW_FILE = "review.md"
EXAMPLE_FILE = "example.md"
FINAL_BLOG_FILE = "final_blog.md"
SUGGESTION = "suggestion.json"


def generate_topics(
    topic: str,
    storage,
    no_topics: int = 5,
    no_subtopics: int = 5,
    debug: bool = False,
    config: Config = None,
) -> TopicsAgentOutput:
    if debug:
        return TopicsAgentOutput(
            answer=read_file(f"{ROOT_DIR}/data/example_topics.json")
        )

    if storage.read(TOPIC_FILE) != "":
        out = TopicsAgentOutput()
        out.topics = load_json(storage.read("topics.json"))
        return out

    stream_callback = StreamConsoleCallbackManager()
    # model_config = new_model_config("mistralai/mistral-7b-instruct:free", llm_type=LLMType.OPEN_ROUTER)
    # model_config = new_model_config("gemini-1.5-pro-latest", llm_type=LLMType.GEMINI)
    model_config = config.model_config_hf_chat
    topic_agent = TopicAgent(
        model_config=model_config,
        stream_callback_manager=stream_callback,
        temperature=0.5,
    )

    output = topic_agent.run(topic, no_topics=no_topics, no_subtopics=no_subtopics)
    storage.write(TOPIC_FILE, json.dumps(output.topics))
    return output


def search_from_topics(
    subject: str, topics: dict, config: Config, storage, debug: bool = False
) -> SearchResult:
    web_scarper = WebScraper(
        config.model_config_hf_chat, config.web_search, config.web_extractor
    )

    model_config = config.model_config_hf_chat
    query_agent = QueryGeneratorAgent(
        model_config=model_config,
        stream_callback_manager=StreamConsoleCallbackManager(),
        temperature=0.5,
    )

    if debug:
        return json.loads(read_file(f"{ROOT_DIR}/data/example_search.json"))

    if storage.read(SEARCH_FILE) != "":

        result = SearchResult()
        result.load_from_json(storage.read(SEARCH_FILE))
        return result

    result = SearchResult()
    outline = dict()

    for _, topic in enumerate(topics):
        search_query = query_agent.run(subject, topic)
        contents = web_scarper.scrape(f"{search_query.content}", topics[topic])
        if len(contents) == 0:
            continue
        outline[topic] = contents
    result.result = outline
    storage.write(SEARCH_FILE, json.dumps(result, cls=ObjectEncoder))
    return result


def write_outline(
    subject: str,
    references: SearchResult,
    storage,
    debug: bool = False,
    config: Config = None,
) -> OutlineModel:
    if debug:
        return read_file(f"{ROOT_DIR}/data/example_writer.txt")

    if storage.read(OUTLINE_FILE) != "":
        data = storage.read(OUTLINE_FILE)
        return OutlineModel.model_validate(from_json(data))

    stream_callback = StreamConsoleCallbackManager()
    model_config = config.model_config_hf_chat
    outline_agent = OutlineAgent(
        model_config=model_config,
        stream_callback_manager=stream_callback,
        temperature=0.1,
    )

    output = outline_agent.run(subject, references)

    description_agent = DescriptionAgent(
        model_config=config.model_config_hf_chat,
        stream_callback_manager=stream_callback,
        temperature=0.1,
    )

    desc_output = description_agent.run(subject, output.raw_response)

    result = json.loads(output.raw_response)
    result["title"] = desc_output.title
    result["description"] = desc_output.description

    storage.write(OUTLINE_FILE, json.dumps(result, cls=ObjectEncoder))
    return OutlineModel(
        title=desc_output.title,
        description=desc_output.description,
        outline=output.outline,
    )


def critique(
    subject: str,
    outline: str,
    completed_part: str,
    current_part: str,
    references: SearchResult,
    debug: bool = False,
    config: Config = None,
) -> WriteCritiqueAgentOutput:
    if debug:
        return read_file(f"{ROOT_DIR}/data/example_writer.txt")

    stream_callback = StreamConsoleCallbackManager()
    model_config = config.model_config_hf_chat
    writer_agent = WriteCritiqueAgent(
        model_config=model_config,
        stream_callback_manager=stream_callback,
        temperature=0.2,
    )

    output = writer_agent.run(
        subject, outline, references, completed_part, current_part
    )
    return output


def write_blog(
    outline_blog,
    outline_output,
    references: SearchResult,
    storage: Storage,
    subject,
    use_critique: bool = False,
    cfg: Config = None,
) -> str:
    blog_content = storage.read(BLOG_FILE)
    if blog_content != "":
        return blog_content
    # write_config = new_model_config(
    #     OpenRouterModel.OR_GOOGLE_GEMMA_7B_IT_FREE.value[0], LLMType.OPEN_ROUTER
    # )

    write_config = cfg.model_config_hf_chat

    # write_config = new_model_config(
    #     OpenRouterModel.PHI_3_MEDIUM.value[0],
    #     LLMType.OPEN_ROUTER,
    # )

    # write_config = new_model_config(OllamaModel.LLAMA3.value, LLMType.OLLAMA)

    # write_config = new_model_config(MODEL_NAME, LLMType.GEMINI)
    writer_agent = WriterAgent(
        model_config=write_config,
        stream_callback_manager=StreamConsoleCallbackManager(),
        temperature=0.5,
    )

    write_with_review = WriterAgent(
        model_config=write_config,
        stream_callback_manager=StreamConsoleCallbackManager(),
        temperature=0.5,
    )

    review_agent = ReviewAgent(
        model_config=write_config,
        stream_callback_manager=StreamConsoleCallbackManager(),
        temperature=0.5,
    )

    extract_relevant_search_agent = ExtractRelevantSearchAgent(
        model_config=write_config,
        stream_callback_manager=StreamConsoleCallbackManager(),
        temperature=0.5,
    )

    example_writer = ExampleWriter(
        model_config=write_config,
        stream_callback_manager=StreamConsoleCallbackManager(),
        temperature=0.1,
    )

    enrichment = EnrichmentAgent()

    first_version = ""
    with_suggestions = ""
    final_blog = ""
    review_blog = ""
    example_blog = ""

    # TODO: remove

    references = None
    tracker = StepTracker()

    try:
        prev_track_record = storage.read(STEP_TRACKER)
        if prev_track_record and prev_track_record.strip() != "":
            tracker = StepTracker.model_validate(from_json(prev_track_record))
    except Exception as e:
        logger.error(f"Fail to track {e}")

    idx = 0
    try:
        for o in outline_output.outline:
            if idx <= tracker.current_step:
                logger.info(f"Skip session has header {o['header']}")
                idx += 1
                continue

            suggestions = ""
            cur_section = f"Header: {o['header']} \n Your content of this section must be written about {o['short_description']}"
            out_content = writer_agent.run(
                topic=subject,
                references=references,
                previous_content=final_blog,
                current_session=cur_section,
                suggestions=suggestions,
            )
            last_content = out_content.content
            first_version += last_content + "\n\n"

            review_output = review_agent.run(
                section=cur_section, section_content=last_content
            )
            review_blog += f"\n\n ## {o['header']} \n\n {review_output.review_msg} \n\n"

            extracted_output = extract_relevant_search_agent.run(
                purpose=cur_section,
                references=references,
                need_to_retrieve=review_output.review_msg,
            )

            # run with suggestions
            out_content = write_with_review.run(
                topic=subject,
                previous_content=final_blog,
                current_session=cur_section,
                suggestions=suggestions,
                retrieved_data=extracted_output.content,
            )
            last_content = out_content.content

            # TODO: enrichment is stop because Bingchat is not working
            # enrichment_output = enrichment.run(
            #     section_topic=cur_section, current_content=last_content
            # )
            # last_content = enrichment_output.content

            # generate example
            example_output = example_writer.run(content=last_content)

            # final result
            with_suggestions += last_content + "\n\n"
            review_blog += f"\n\n ### Questions follow \n\n {suggestions} \n\n"
            final_blog += last_content + "\n\n"
            example_blog += f"\n\n### Example \n\n {o['header']} \n\n======= \n\n {example_output.content}\n\n======= \n\n"
            tracker.current_step = idx
            idx += 1
    except Exception as e:
        logger.error(e)

    storage.write(STEP_TRACKER, tracker.model_dump_json())
    storage.write(BLOG_V1_FILE, first_version)
    storage.write(BLOG_V2_FILE, with_suggestions)
    storage.write(BLOG_FILE, final_blog)
    storage.write(REVIEW_FILE, review_blog)
    storage.write(EXAMPLE_FILE, example_blog)
    return final_blog


def enrich_topic(subject: str):
    config = new_model_config(LLMType.BING_CHAT, LLMType.BING_CHAT)
    enrichTopicAgent = EnrichTopic(
        model_config=config,
    )
    output = enrichTopicAgent.run(subject=subject)
    return output.answer


def generate(subject, load_from, skip_all: bool = True):
    config = load_config()
    subject = subject.strip()
    # subject = enrich_topic(subject)

    storage = Storage(subject, load_from_workspace=load_from)

    storage.write(SUBJECT, subject)

    output = generate_topics(subject, storage, 5, 10, False, config)
    if not skip_all:
        continue_ok = input("Search: Press Enter to continue...")
        if continue_ok != "y":
            logger.info(storage.workspace)
            return

    # TODO: disable search
    # references = search_from_topics(subject, output.topics, config, storage, False)
    references = None
    outline_output: OutlineModel = write_outline(
        subject, references, storage, False, config
    )

    if not skip_all:
        continue_ok = input("Outline: Press Enter to continue...")
        if continue_ok != "y":
            logger.info(storage.workspace)
            return

    outline_blog = json.dumps(outline_output.outline)
    blog_content = write_blog(
        outline_blog=outline_blog,
        outline_output=outline_output,
        references=references,
        storage=storage,
        subject=subject,
        use_critique=False,
        cfg=config,
    )

    if storage.read(SUGGESTION) != "":
        logger.info("Suggestion already generated")
    else:
        write_config = config.model_config_hf_chat
        suggest_agent = SuggestionAgent(
            model_config=write_config,
            stream_callback_manager=StreamConsoleCallbackManager(),
            temperature=0.1,
        )
        output = suggest_agent.run(subject, blog_content)
        logger.info(output.content)
        storage.write(SUGGESTION, output.content)

    storage.write(FINAL_BLOG_FILE, fix_format(storage))

    isGenImage = input("Generate image? y/n: ")
    if isGenImage == "y":
        logger.info("Start generate image")
        image_generate_agent = ImageGeneratorAgent(
            model_config=config.model_config_hf_chat,
        )
        image_generate_agent.run(outline_output.description, storage.working_name)
        logger.info("Gen image done")


if __name__ == "__main__":
    problem = read_file("../../input.txt")
    subject = f'Write a blog about\n"""{problem}\n"""'
    load_from = ""
    generate(subject, load_from)
