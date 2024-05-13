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
    
    lines = data.split("\n")
    found = False
    new_data = ""
    for line in lines:
        if found:
            new_data += line + "\n"
        if line.startswith("```"):
            found = True
            new_data += line + "\n"
            continue
    
    if new_data == "":
        return data
    
    data = new_data.strip()
    
    if "```\n{" in data:
        data = data.replace("```\n{", "```json\n{")
    if "```JSON" in data:
        val = data.replace("```JSON", "").replace("```json", "")
    val = re.findall(r'```json(.*?)```', data, re.DOTALL)
    if len(val) == 0:
        val = re.findall(r'```(.*?)```', data, re.DOTALL)

    return val[0] if val else data

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
