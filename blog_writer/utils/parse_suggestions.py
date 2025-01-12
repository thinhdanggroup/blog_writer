import json

from typing import List

import subprocess

import os

from blog_writer.config.logger import logger
from blog_writer.utils.text import load_json, extract_json_from_markdown


INDEX_FILE = "index.json"


def persist_suggestions(raw: str, output_path: str) -> str:
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    with open(f"{output_path}/raw.json", "w") as file:
        file.write(raw)

    raw = extract_json_from_markdown(raw)
    json_data = load_json(raw)

    suggestion_files = []
    suggestions = json_data.get("suggestions", [])
    output_suggestions = ""

    i = 0

    if "code_snippets" in suggestions:
        for code_snippet in suggestions["code_snippets"]:
            i += 1
            with open(f"{output_path}/snippet_{i}.md", "w") as file:
                file.write(code_snippet.get("code", ""))

    if "images" in suggestions:
        for image in suggestions["images"]:
            i += 1
            with open(f"{output_path}/image_{i}.md", "w") as file:
                file.write(image.get("image", "") + "\n" + image.get("description", ""))

    if "diagrams" in suggestions:
        for diagram in suggestions["diagrams"]:
            i += 1
            file_prefix = f"{output_path}/diagram_{i}"
            with open(f"{file_prefix}.mermaid", "w") as file:
                diagram_content = diagram.get("diagram", "")
                diagram_content = diagram_content.replace("```mermaid", "").replace(
                    "```", ""
                )
                file.write(diagram_content)
                logger.info(f"Generating diagram {file_prefix}.png")

            # run command mmdc -i diagram_1.mermaid -o diagram_1.png
            subprocess.run(
                [
                    "mmdc",
                    "-i",
                    f"{file_prefix}.mermaid",
                    "-o",
                    f"{file_prefix}.png",
                ]
            )

            output_suggestions += f"![{file_prefix}.png]({file_prefix}.png)\n"
            suggestion_files.append(f"{file_prefix}.png")

    with open(f"{output_path}/{INDEX_FILE}", "w") as file:
        file.write(json.dumps(suggestion_files))

    return output_suggestions
