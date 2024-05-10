import os

from typing import Any

def print_formatted_log(**kwargs: Any):
    print("-" * 50)
    for key, value in kwargs.items():
        if key == "color":
            continue

        print(f"{key}: {value}\n")
    print("-" * 50)


def read_file(file_path):
    print_formatted_log(action="read_file", file_path=file_path, color="red")
    try:
        with open(file_path, "r") as f:
            file_content = f.read()
        return file_content
    except FileNotFoundError:
        print(f"# File not found {file_path}")
        # raise FileNotFoundError
    except IOError:
        print("Error occurred while updating the file.")
    return ""


def append_file(file_path, content):
    print(f"Writing file {file_path}")

    parent_folder = os.path.dirname(file_path)

    if not os.path.exists(parent_folder):
        os.makedirs(parent_folder)

    try:
        with open(file_path, "a") as file:
            file.write(content)
        print("File updated successfully.")
    except FileNotFoundError:
        print(f"File not found {file_path}")
        raise FileNotFoundError
    except IOError:
        print("Error occurred while updating the file.")
