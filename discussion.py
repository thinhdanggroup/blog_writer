import json

from blog_writer.agents.writer import WriterAgent
from blog_writer.config.config import new_model_config, load_config
from blog_writer.store.storage import Storage
from blog_writer.utils.stream_console import StreamConsoleCallbackManager
from blog_writer.utils.text import load_json


def main():
    config = load_config()
    workspace = "231115205402_write_a_blog_about_-"
    storage = Storage("", load_from_workspace=workspace)
    outline = storage.read("outline.json")
    outline_blog = load_json(outline)
    subject = outline_blog["description"]

    references = storage.read("search.json")
    cur_blog = storage.read("blog.md")
    suggestions = ""
    final_blog = storage.read("final_blog.md")

    write_config = new_model_config("gpt-4-32k-0613")
    writer_agent = WriterAgent(model_config=write_config, stream_callback_manager=StreamConsoleCallbackManager(),
                               temperature=0.5)

    out_content = writer_agent.run(subject, references, cur_blog,
                                   "Write a example for the blog that break online shop in monolithic to microservices",
                                   suggestions)
    print("=== Rewrite Session ===")
    print(out_content.content)
    storage.write("example_1.md", out_content.content)


if __name__ == "__main__":
    main()
