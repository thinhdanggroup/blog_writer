import os

import json
import re

from blog_writer.config.definitions import INDEX_DIAGRAM
from blog_writer.store.storage import Storage
from blog_writer.utils.text import load_json


DATA_OUTPUT = """---
author:
    name: "Thinh Dang"
    avatar: "/assets/images/avatar.png"
    bio: "Experienced Fintech Software Engineer Driving High-Performance Solutions"
    location: "Viet Nam"
    email: "thinhdang206@gmail.com"
    links:
        -   label: "Linkedin"
            icon: "fab fa-fw fa-linkedin"
            url: "https://www.linkedin.com/in/thinh-dang/"
toc: true
toc_sticky: true
header:
    overlay_image: /assets/images/{{blog-tag}}/banner.jpeg
    overlay_filter: 0.5
    teaser: /assets/images/{{blog-tag}}/banner.jpeg
title: "{{title}}"
tags:
    - xxx
    - yyy 

---"""


def remove_references(text):
    return re.sub(r"\[\^.*?\^\]", "", text)


def detect_references(text):
    pattern = r"\[\^.*?\^\]: \[.*?\]\(.*?\)"
    matches = re.findall(pattern, text)
    return matches


def extract_reference_details(text):
    pattern = r"\[\^(.*?)\^\]: \[(.*?)\]\((.*?)\)"
    matches = re.findall(pattern, text)
    if len(matches) == 0:
        return None

    return matches[0]


def create_final_format(storage):
    PARENT_FINAL_FOLDER = "final"

    FINAL_BLOG_FILE = f"{PARENT_FINAL_FOLDER}/final_blog.md"
    storage.write(FINAL_BLOG_FILE, fix_format(storage))


def fix_format(storage):
    blog_content = storage.read("blog.md")
    o = storage.read("outline.json")
    outline = load_json(o)

    final_content = ""

    first_session = DATA_OUTPUT.replace("{{title}}", outline["title"])
    first_session = first_session.replace("{{blog-tag}}", storage.generated_name)
    final_content += first_session + "\n\n"
    final_content += f"{outline['description']}\n\n"

    list_references = set()

    main_index = json.loads(storage.read(INDEX_DIAGRAM))

    for current_session in main_index:
        sub_folder_name = current_session["sub_folder_name"]
        last_content = current_session["content"]
        if last_content.startswith("```markdown"):
            last_content = last_content.replace("```markdown", "")
            # replace last ``` with empty string
            last_content = last_content[: last_content.rfind("```")]

        # insert data after first line
        split_content = last_content.split("\n")

        # find index of #
        index = 0
        for i, v in enumerate(split_content):
            if v.startswith("#"):
                index = i
                break

        split_content.insert(index + 1, read_png_files(storage, sub_folder_name))
        last_content = "\n".join(split_content)

        final_content += last_content + "\n\n"

    final_content = remove_references(final_content)
    final_content = create_references(final_content, list_references)

    return final_content


def read_png_files(storage, sub_folder_name) -> str:
    index_arr = json.loads(storage.read(f"{sub_folder_name}/index.json"))
    list_png_files = []

    # list file in sub folder
    for file in storage.list(f"{sub_folder_name}"):
        if file.endswith(".png"):
            list_png_files.append(file)

    value_path = ""
    working_image_path = f"{storage.workspace}/{sub_folder_name}"
    image_root_path = f"/assets/images/{storage.generated_name}"
    final_working_image_path = f"{storage.workspace}/final/{storage.generated_name}"

    os.makedirs(final_working_image_path, exist_ok=True)

    for file in list_png_files:
        new_file_name = f"{sub_folder_name}_{file}"
        # copy file -> assets/images
        os.system(
            f"cp {working_image_path}/{file} {final_working_image_path}/{new_file_name}"
        )

        # new path = /assets/images/working_name/sub_folder_name/file
        value_path += f"\n![{new_file_name}]({image_root_path}/{new_file_name})\n"
    return value_path


def create_references(final_content, list_references):
    if len(list_references) > 0:
        final_content += "\n\n## References\n\n"
        sorted_matches = sorted(list_references, key=lambda x: int(x[0]))

        update_refs = []
        for v in sorted_matches:
            if v in update_refs:
                continue
            final_content += f"- [{v[1]}]({v[2]}) \n"
            update_refs.append(v[2])
    return final_content


def fix_file(workspace):
    storage = Storage("", load_from_workspace=workspace)
    fix_format(storage)


if __name__ == "__main__":
    storage = Storage(
        subject="blog-on-sip-trunking-communication",
        load_from_workspace="250112123241_blog-on-sip-trunking-communication-",
    )
    storage.generated_name = "blog-on-sip-trunking-communication"
    create_final_format(storage)
