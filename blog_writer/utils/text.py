import json
import re

from blog_writer.config.logger import logger


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
    if not data.startswith("```"):
        return data
    if "```JSON" in data:
        val = data.replace("```JSON", "").replace("```json", "")
    val = re.findall(r'```json(.*?)```', data, re.DOTALL)
    if len(val) == 0:
        val = re.findall(r'```(.*?)```', data, re.DOTALL)

    return val[0] if val else data


if __name__ == "__main__":
    input_val = """```
{
    "topics": [
        {
            "topic": "Overview of the Gemini Model",
            "subtopics": [
                "Introduction to the Gemini Model",
                "Key Components of the Gemini Model",
                "Benefits and Applications of the Gemini Model"
            ]
        },
        {
            "topic": "Architecture and Implementation of the Gemini Model",
            "subtopics": [
                "High-Level Architecture of the Gemini Model",
                "Key Implementation Details and Challenges",
                "Scalability and Performance Considerations"
            ]
        },
        {
            "topic": "Training and Fine-Tuning the Gemini Model",
            "subtopics": [
                "Data Preparation and Preprocessing for Training",
                "Selection of Hyperparameters and Optimization Techniques",
                "Strategies for Fine-Tuning and Transfer Learning"
            ]
        },
        {
            "topic": "Applications and Use Cases of the Gemini Model",
            "subtopics": [
                "Natural Language Processing and Text Generation",
                "Machine Translation and Multilingual Tasks",
                "Question Answering and Information Retrieval"
            ]
        },
        {
            "topic": "Recent Advancements and Future Directions in the Gemini Model",
            "subtopics": [
                "Integration with Other Language Models and Architectures",
                "Exploration of Multimodal and Multitask Learning",
                "Ethical and Societal Implications of the Gemini Model"
            ]
        }
    ]
}
```"""
    print(extract_json_from_markdown(input_val))
