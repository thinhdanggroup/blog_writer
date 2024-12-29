import os
from typing import sys, List

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from blog_writer.config.config import load_config
from blog_writer.utils.llm import create_chat_model
from blog_writer.utils.stream_console import StreamConsoleCallbackManager
from blog_writer.utils.stream_token_handler import StreamTokenHandler
from utils import read_file, append_file
from blog_writer.config.config import new_model_config
from blog_writer.config.definitions import LLMType, OpenRouterModel
from blog_writer.config.definitions import TSModel
import streamlit as st
import pyperclip

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_all_prompts() -> List[str]:
    test_cases = []
    for usecase in os.listdir(f"{ROOT_DIR}/reviews/peers"):
        # check if usecase is a directory
        if os.path.isdir(f"{ROOT_DIR}/reviews/peers/{usecase}"):
            test_cases.append(usecase)
    return test_cases


def get_all_questions() -> List[str]:
    test_cases = []
    for usecase in os.listdir(f"{ROOT_DIR}/reviews/questions"):
        # check if usecase is a directory
        if not os.path.isdir(f"{ROOT_DIR}/reviews/questions/{usecase}"):
            test_cases.append(usecase)

    test_cases.sort()
    print(test_cases)
    return test_cases

def copy_to_clipboard(text):
    pyperclip.copy(text)
    st.toast("Copied to clipboard!")

def generate(system_msgs,questions,llm,selected="default"):
    # Initialize answers in session state if not exists
    if 'answers' not in st.session_state:
        st.session_state.answers = {}

    for question in questions:
        st.text("========================================")

        append_file(
            f"{ROOT_DIR}/reviews/output/{selected}/backup.txt",
            "\n========================================\n",
            log=False,
        )

        message = read_file(f"{ROOT_DIR}/reviews/questions/{question}")
        print(f"Question: {message}")

        chain_msgs = system_msgs.copy()
        chain_msgs.append(HumanMessage(content=message))
        st.text(f"Question: {message}")
        append_file(
            f"{ROOT_DIR}/reviews/output/{selected}/backup.txt",
            f"Question:\n{message}",
            log=False,
        )
        res = StreamTokenHandler(llm)(chain_msgs, False)
        append_file(
            f"{ROOT_DIR}/reviews/output/{selected}/backup.txt",
            f"Answer:\n{res}",
            log=False,
        )

        # Store answer in session state
        answer_key = f"answer_{hash(question)}"
        st.session_state.answers[answer_key] = res

        # Display answer with copy button
        col1, col2 = st.columns([0.95, 0.05])
        st.text_area("Answer:", value=res, height=500, key=answer_key, disabled=False)

        system_msgs.append(
            AIMessage(content=f"History: last question {message} with answer {res}")
        )


def main():
    cfg = load_config()
    questions = get_all_questions()

    selected = "default"
    st.title("Peer Review")

    system = st.text_area("System", value=read_file(f"{ROOT_DIR}/reviews/system_ui.txt"),
    height=500)
    system += f"\n\n[[profile]]"

    profile = st.text_area("Profile", value=read_file(f"{ROOT_DIR}/reviews/peers/{selected}/readme.md"),
    height=500)

    # [[profile]]
    system = system.replace(
        "[[profile]]", profile
    )
    # message = read_file(f"{ROOT_DIR}/reviews/peers/{selected}/human.txt")

    callback = StreamConsoleCallbackManager()

    config = new_model_config(
        TSModel.GPT_4O.value,
        LLMType.TS_CHAT,
    )

    llm = create_chat_model(
        model_config=config,
        temperature=0,
        stream_callback_manager=callback,
    )

    system_msgs = [SystemMessage(content=system)]

    st.button(
        "run",
        on_click=generate,
        args=(system_msgs,questions,llm),
    )
        


if __name__ == "__main__":
    main()
