from langchain.schema import SystemMessage, HumanMessage, AIMessage

from blog_writer.config.config import load_config
from blog_writer.utils.llm import create_chat_model
from blog_writer.utils.stream_console import StreamConsoleCallbackManager
from blog_writer.web_scraper.extractor import WebExtractor


def get_system_prompt():
    return """You are research assistant that received a data from human and answer the question.
    """

def beautiful_print(text):
    print("========================================")
    print(text)
    print("========================================")

def main():
    print("Start chatbot...\n")
    cfg = load_config()
    web_extractor = WebExtractor(cfg.web_extractor, cfg.model_config)
    cfg.model_config.deployment = "gpt4-32k"
    llm = create_chat_model(
        temperature=0.1,
        model_config=cfg.model_config,
        max_tokens=2000,
        stream_callback_manager=StreamConsoleCallbackManager()
    )

    messages = [SystemMessage(content=get_system_prompt())]
    while True:
        user_input = input("You: ")

        if user_input == "exit":
            break

        if user_input.startswith("check"):
            parsed = user_input.strip().split(" ")
            if len(parsed) != 2:
                beautiful_print("Invalid command")
                continue
            url = parsed[1]
            doc = web_extractor.get_content(url)

            beautiful_print(doc)
            messages.append(AIMessage(content=f"A web content that you have to reference: {doc}"))
            continue

        messages.append(HumanMessage(content=user_input))
        message = llm(messages)
        beautiful_print(message.content)
        messages.append(AIMessage(content=message.content))


if __name__ == "__main__":
    main()
