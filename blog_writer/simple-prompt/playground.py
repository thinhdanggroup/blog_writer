import os
from typing import List

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from blog_writer.config.config import load_config
from blog_writer.utils.llm import create_chat_model
from blog_writer.utils.stream_console import StreamConsoleCallbackManager
from blog_writer.utils.stream_token_handler import StreamTokenHandler
from utils import read_file, append_file
from blog_writer.config.config import new_model_config
from blog_writer.config.definitions import LLMType, OpenRouterModel

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_all_prompts() -> List[str]:
    test_cases = []
    for usecase in os.listdir(f"{ROOT_DIR}/prompts"):
        # check if usecase is a directory
        if os.path.isdir(f"{ROOT_DIR}/prompts/{usecase}"):
            test_cases.append(usecase)
    return test_cases


def main():
    cfg = load_config()
    usecases = get_all_prompts()
    print("Select a usecase:")
    for i, usecase in enumerate(usecases):
        print(f"{i + 1}. {usecase}")

    # hardcode
    default_select = 2
    if default_select == 0:
        selected = int(input("Enter a number: "))
    else:
        selected = default_select
    selected = usecases[selected - 1]

    system = read_file(f"{ROOT_DIR}/prompts/{selected}/system.txt")
    message = read_file(f"{ROOT_DIR}/prompts/{selected}/human.txt")

    callback = StreamConsoleCallbackManager()

    config = new_model_config(
        # "gemini-pro",LLMType.GEMINI
        # OpenRouterModel.OR_MISTRALAI_MISTRAL_7B_INSTRUCT_FREE.value[0], LLMType.OPEN_ROUTER
        LLMType.BING_CHAT, LLMType.BING_CHAT
    )
    llm = create_chat_model(
        model_config=config,
        temperature=0,
        stream_callback_manager=callback,
        # use_json_format=True,
    )

    chain_msgs = [SystemMessage(content=system), HumanMessage(content=message)]

    while True:
        append_file(f"{ROOT_DIR}/output/{selected}/backup.txt", f"Question:\n{message}")
        res = StreamTokenHandler(llm)(chain_msgs)
        print("========================================")
        append_file(f"{ROOT_DIR}/output/{selected}/backup.txt", f"Answer:\n{res}")
        # print(res)
        # print("========================================")
        message = input("Enter message: ")
        chain_msgs.append(AIMessage(content=res))
        chain_msgs.append(HumanMessage(content=message))


if __name__ == "__main__":
    main()
