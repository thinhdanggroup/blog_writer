import json
import re

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
    overlay_image: /assets/images/xxx/banner.jpeg
    overlay_filter: 0.5
    teaser: /assets/images/xxx/banner.jpeg
title: {{title}}
tags:
    - xxx
    - yyy 

---"""


def remove_references(text):
    return re.sub(r'\[\^.*?\^\]', '', text)


def detect_references(text):
    pattern = r'\[\^.*?\^\]: \[.*?\]\(.*?\)'
    matches = re.findall(pattern, text)
    return matches


def extract_reference_details(text):
    pattern = r'\[\^(.*?)\^\]: \[(.*?)\]\((.*?)\)'
    matches = re.findall(pattern, text)
    if len(matches) == 0:
        return None

    return matches[0]


def fix_format(storage):
    blog_content = storage.read("blog.md")
    o = storage.read("outline.json")
    outline = load_json(o)

    final_content = ""
    
    final_content += DATA_OUTPUT.replace("{{title}}", outline['title']) + "\n\n"
    final_content += f"{outline['description']}\n\n"

    list_references = set()
    for text in blog_content.splitlines():
        is_references = detect_references(text)
        if is_references:
            list_references.add(extract_reference_details(text))
        else:
            if text.startswith("#"):
                text = text.replace("# ", "## ", 1)
            final_content += text + "\n"

    final_content = remove_references(final_content)
    final_content += "\n\n## References\n\n"

    sorted_matches = sorted(list_references, key=lambda x: int(x[0]))
    update_refs = []
    for v in sorted_matches:
        if v in update_refs:
            continue
        final_content += f"- [{v[1]}]({v[2]}) \n"
        update_refs.append(v[2])

    print(final_content)
    return final_content


def fix_file(workspace):
    storage = Storage("", load_from_workspace=workspace)
    fix_format(storage)


if __name__ == "__main__":
    fix_file("230827190423_write_a_blog_about_f")
