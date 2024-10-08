import json
import re

from blog_writer.config.logger import logger
import tiktoken


def load_json(data: str, throw_if_err: bool = False) -> dict:
    """
    Load JSON from string and return a dict.

    Args:
        data: str

    Returns:
        dict
    """
    try:
        json_data = extract_json_from_markdown(data)
        json_data = ignore_first_path(json_data)
        data = json.loads(json_data)
        return data
    except json.JSONDecodeError as e:
        logger.error("Error when loading JSON: %s data %s", e, data, exc_info=True)
        if throw_if_err:
            raise e
        return {}


def extract_json_from_markdown(data: str) -> str:
    """
    Extract JSON from markdown file and return a string. json is enclosed in ```json``` or ``````.

    Args:
        data: str

    Returns:
        str
    """
    data = data.strip()

    if "```\n{" in data:
        data = data.replace("```\n{", "```json\n{")
    if "```JSON" in data:
        data = data.replace("```JSON", "").replace("```json", "")
    if "```json\n" in data:
        data = data.replace("```json\n", "")
        # replace last ``` with empty string
        data = data.rsplit("```", 1)[0].strip()
        return data

    # count ``` in data
    count = data.count("```")
    if count > 2:
        return data

    logger.info("Parsing data: %s", data)
    return data
    #
    # val = re.findall(r"```json(.*?)```", data, re.DOTALL)
    # if len(val) == 0:
    #     val = re.findall(r"```(.*?)```", val, re.DOTALL)
    #
    # return val[0] if val else data


def extract_content_from_markdown(data: str) -> str:
    if not data.startswith("```"):
        return data

    data = data.replace("```markdown", "")
    data = data.replace("```md", "")
    # replace last ``` with empty string
    data = data.rsplit("```", 1)[0]
    return data


def ignore_first_path(data: str) -> str:
    if data.startswith("{"):
        return data

    # get data from first { to last }
    start = data.find("{")
    end = data.rfind("}")
    return data[start : end + 1]


def count_tokens(tokens: str) -> int:
    enc = tiktoken.encoding_for_model("gpt-4")
    total = len(enc.encode(tokens))
    return total


if __name__ == "__main__":
    input_val = """{
  "questions": [
    {
      "question": "What are Ollama models and how do they work?",
      "has_answer": false
    },
    {
      "question": "Key features and benefits of using Ollama models",
      "has_answer": false
    },
    {
      "question": "Different types of Ollama models and their specific use cases",
      "has_answer": false
    },
    {
      "question": "Comparison of Ollama models with other language models like LLaMA, GPT",
      "has_answer": false
    },
    {
      "question": "Limitations of Ollama models and areas for improvement",
      "has_answer": false
    }
  ]
}"""
    # extracted_data = extract_json_from_markdown(input_val)
    print(json.loads(input_val))
