import os

from blog_writer.utils.parse_suggestions import persist_suggestions


def test_parse_uml():
    base_path = "../.working_space/240924222223_guide-on-git-versioning-"

    # list all folders in path
    folders = os.listdir(base_path)

    for folder in folders:
        if not os.path.isdir(f"{base_path}/{folder}"):
            break

        with open(f"{base_path}/{folder}/raw.json", "r") as file:
            data = file.read()

        persist_suggestions(raw=data, output_path=f"{base_path}/{folder}")
