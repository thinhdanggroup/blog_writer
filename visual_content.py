import markdown
from bs4 import BeautifulSoup

from blog_writer.agents.suggestion import SuggestionAgent
from blog_writer.config.config import load_config
from blog_writer.utils.parse_suggestions import persist_suggestions
from blog_writer.utils.stream_console import StreamConsoleCallbackManager


def parse_markdown_by_section(markdown_content):
    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_content)

    # Parse HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    sections = {}
    current_section = None

    title = [
        "Introduction",
        "1. Simple Atomic Lock",
        "2. Expiring Lock",
        "3. Redlock Algorithm",
        "4. Semaphore",
        "5. Fair Lock",
        "6. Read-Write Lock",
        "7. Reentrant Lock",
        "8. Multi-key Lock",
        "9. Zookeeper-style Lock",
        "10. Lease Lock",
        "Summary Table",
    ]
    for element in soup:
        if (
            element.name
            and element.name.startswith("h2")
            and element.get_text() in title
        ):
            current_section = element.get_text()
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(str(element))

    # print(title)

    # Convert lists to strings
    for section in sections:
        sections[section] = "".join(sections[section])

    return sections


def main():
    file_path = "/Users/thinh.dang2/Documents/personal/thinhdanggroup.github.io/_posts/2024-08-01-10-redis-locks.md"
    with open(file_path, "r") as file:
        file_content = file.read()

    config = load_config()

    suggest_agent = SuggestionAgent(
        model_config=config.model_config_ts_chat,
        stream_callback_manager=StreamConsoleCallbackManager(),
        temperature=0.1,
    )
    output_path = ".working_space/test"
    sections = parse_markdown_by_section(file_content)
    for section, content in sections.items():
        print(f"Section: {section}\n")

        res = suggest_agent.run(content)
        # print(res.content)
        persist_suggestions(res.content, output_path + f"/{section}")

        # pass


if __name__ == "__main__":
    main()
#     data = """```json
# {
#     "is_ok": false,
#     "suggestions": {
#         "code_snippets": [
#             {
#                 "code": "```python\nimport redis\nimport uuid\nimport time\n\nclass ZookeeperStyleLock:\n    def __init__(self, redis_client, lock_name, ttl=10000):\n        self.redis_client = redis_client\n        self.lock_name = lock_name\n        self.ttl = ttl\n        self.lock_id = str(uuid.uuid4())\n\n    def acquire(self):\n        while True:\n            # Try to create a unique node with an expiration time\n            if self.redis_client.set(self.lock_name, self.lock_id, nx=True, px=self.ttl):\n                return True\n            # Wait for a short period before retrying\n            time.sleep(0.1)\n\n    def release(self):\n        # Ensure that only the client that acquired the lock can release it\n        if self.redis_client.get(self.lock_name) == self.lock_id:\n            self.redis_client.delete(self.lock_name)\n\n# Example usage\nredis_client = redis.StrictRedis(host='localhost', port=6379)\nlock_name = \"zookeeper-style-lock\"\nzookeeper_lock = ZookeeperStyleLock(redis_client, lock_name)\n\n# Acquiring the lock\nif zookeeper_lock.acquire():\n    try:\n        # Critical section\n        print(\"Lock acquired, performing operations.\")\n    finally:\n        zookeeper_lock.release()\n        print(\"Lock released.\")\n```",
#                 "description": "A complete and properly formatted code snippet demonstrating the implementation of Zookeeper-style locks using Redis. This snippet includes class definition, methods for acquiring and releasing the lock, and an example usage."
#             }
#         ],
#         "images": [
#             {
#                 "image": "distributed_locking_diagram.png",
#                 "description": "A diagram illustrating the concept of Zookeeper-style locks. It should show multiple clients attempting to acquire a lock, the creation of unique ephemeral nodes, and the automatic release of locks when a client session ends."
#             }
#         ],
#         "diagrams": [
#             {
#                 "diagram": "sequenceDiagram\n    participant Client1\n    participant Client2\n    participant Zookeeper\n    Client1->>Zookeeper: Create ephemeral node with UUID\n    Client2->>Zookeeper: Attempt to create ephemeral node\n    Zookeeper-->>Client2: Wait (node exists)\n    Client1-->>Zookeeper: Release ephemeral node\n    Zookeeper-->>Client2: Node created\n    Client2->>Zookeeper: Create ephemeral node with UUID",
#                 "description": "A sequence diagram showing the process of acquiring and releasing a Zookeeper-style lock. It visualizes the interactions between multiple clients and the Zookeeper ensemble, highlighting the orderly lock acquisition and release process."
#             }
#         ]
#     }
# }
# ```
# """
#     print(parse_suggestions(data, ".working_space/test"))
