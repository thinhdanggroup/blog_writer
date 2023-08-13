from blog_writer.utils.file import read_file
from blog_writer.config.definitions import ROOT_DIR


def load_agent_prompt(prompt):
    prompt_msg = read_file(f"{ROOT_DIR}/blog_writer/prompts/{prompt}.txt")
    if not prompt_msg:
        raise ValueError(f"Prompt {prompt} not found")

    return prompt_msg


