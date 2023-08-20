import os
import re
import uuid
from datetime import datetime

from blog_writer.config.logger import logger


def list_files(startpath):
    full_path_list = {}
    relative_path_list = []

    for root, dirs, files in os.walk(startpath):
        if ".venv" in dirs:
            dirs.remove(".venv")
        if ".git" in dirs:
            dirs.remove(".git")

        for f in files:
            full_path_list[f] = os.path.join(root, f)
            if ".pyc" in f:
                continue
            if ".gitignore" in f:
                continue
            relative_path_list.append(f)
    return full_path_list, relative_path_list


def read_file(file_path):
    logger.info(f"Reading file {file_path}")
    try:
        with open(file_path, "r") as f:
            file_content = f.read()
        return file_content
    except FileNotFoundError:
        logger.error("# File not found %s", file_path)
    except IOError:
        logger.info("Error occurred while updating the file.")
    return ""


def remove_file(file_path):
    logger.info(f"Remove file {file_path}")
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"{file_path} has been removed successfully.")
        except OSError as e:
            logger.error(f"{file_path} could not be removed. {e}")
    else:
        logger.error(f"{file_path} does not exist.")


def create_file_with_path(file_path):
    parent_folder = os.path.dirname(file_path)

    if not os.path.exists(parent_folder):
        os.makedirs(parent_folder)

    with open(file_path, "w"):
        pass


def write_file(file_path, content):
    logger.info(f"Writing file {file_path}")

    parent_folder = os.path.dirname(file_path)

    if not os.path.exists(parent_folder):
        os.makedirs(parent_folder)

    try:
        with open(file_path, "w") as file:
            file.write(content)
        logger.info("File updated successfully.")
    except FileNotFoundError:
        logger.error(f"File not found {file_path}")
        raise FileNotFoundError
    except IOError:
        logger.error("Error occurred while updating the file.")


def append_file(file_path, content):
    logger.info(f"Append file {file_path}")

    parent_folder = os.path.dirname(file_path)

    if not os.path.exists(parent_folder):
        os.makedirs(parent_folder)

    try:
        with open(file_path, "a") as file:
            file.write(content)
        logger.info("File updated successfully.")
    except FileNotFoundError:
        logger.error(f"File not found {file_path}")
        raise FileNotFoundError
    except IOError:
        logger.error("Error occurred while updating the file.")


def generate_file_name():
    date_str = datetime.now().strftime("%Y-%m-%d")
    unique_id = uuid.uuid4()
    file_name = f"{date_str}-{unique_id}.txt"
    return file_name


def write_code_to_file(file: str, code: str):
    logger.info(f"Writing code to file {file} \n code {code}")
    if not code:
        logger.error("nothing to write")
        return
    with open(file, "w") as f:
        f.write(code)
        f.write("\n")


def extract_code_block(s: str):
    pattern = r"```.*?\n(.*?)\n```"
    match = re.search(pattern, s, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return ""


def extract_two_code_block(s: str):
    pattern = r"```.*?\n(.*?)\n```"
    # Find all matches of code blocks in the string
    matches = re.findall(pattern, s, re.DOTALL)

    if len(matches) == 0:
        return "", ""

    code_block_1 = matches[0]
    if len(matches) == 1:
        return code_block_1, ""

    code_block_2 = matches[1]
    return code_block_1, code_block_2


def extract_code_and_unittest(input_str: str):
    solution_str = "SOLUTION:"
    fixed_code_str = "FIXED_CODE:"
    unit_test_str = "UNIT_TEST:"

    start_index = input_str.index(solution_str) + len(solution_str)
    end_index = input_str.index(fixed_code_str)
    solution = input_str[start_index:end_index]

    start_index = input_str.index(fixed_code_str) + len(fixed_code_str)
    end_index = input_str.index(unit_test_str)

    fixed_code = input_str[start_index:end_index].strip()

    start_index = end_index + len(unit_test_str)
    unit_test = input_str[start_index:].strip()

    return solution, extract_code_block(fixed_code), extract_code_block(unit_test)


def parse_relative_workspace_file_name(path: str):
    if "workspace/worktree" in path:
        return "/".join(path.split("/")[4:])

    if "workspace" in path:
        return "/".join(path.split("/")[2:])

    return path


def get_main_space(working_space) -> (str, bool):
    if "workspace/worktree" not in working_space:
        return working_space, False
    return "workspace/" + working_space.split("/")[2], True


def read_code_bases(working_space: str):
    code_bases = []
    if "workspace/worktree" in working_space:
        code_bases.append("workspace")
    code_bases.append(working_space)
    return code_bases

def wrap_text_with_tag(text: str, tag: str) -> str:
    return f"<{tag}>\n{text}\n</{tag}>\n"