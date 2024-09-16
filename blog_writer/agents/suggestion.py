import json
from typing import List, Tuple, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from blog_writer.agents.base import AgentInterface
from blog_writer.config.config import load_config
from blog_writer.config.logger import logger
from blog_writer.model.search import SearchResult
from blog_writer.prompts import load_agent_prompt
from blog_writer.utils.encoder import ObjectEncoder
from blog_writer.utils.file import wrap_text_with_tag
from blog_writer.utils.stream_token_handler import StreamTokenHandler


class SuggestionAgentOutput:
    def __init__(self, answer: str = ""):
        self.content = answer


class SuggestionAgent(AgentInterface):
    def render_system_message(self):
        system_message = SystemMessage(content=load_agent_prompt("suggestion"))
        return system_message

    def render_human_message(
        self,
        blog: str,
    ):
        content = wrap_text_with_tag(blog, "blog")
        logger.info(
            "\033[31m****Suggestion Agent human message****\n%s\033[0m", content
        )
        return HumanMessage(content=content)

    def run(
        self,
        blog: str,
    ) -> SuggestionAgentOutput:
        human_message = self.render_human_message(
            blog=blog,
        )

        messages = [
            self.render_system_message(),
            human_message,
        ]

        content = self.call_llm(messages)
        ai_message = f"{content}\n"
        return SuggestionAgentOutput(ai_message)


if __name__ == "__main__":
    config = load_config()
    agent = SuggestionAgent(model_config=config.model_config_ts_chat)
    output = agent.run(
        """
### Write-Around Caching

In the write-around caching pattern, data is written directly to the backing store, bypassing the cache. This pattern is useful for write-heavy workloads where caching write operations may not be necessary.

#### Example: Write-Around Caching in Python

```python
class WriteAroundCache:
    def __init__(self, backing_store):
        self.cache = {}
        self.backing_store = backing_store

    def set(self, key, value):
        # Write directly to backing store
        self.backing_store[key] = value

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        elif key in self.backing_store:
            value = self.backing_store[key]
            self.cache[key] = value
            return value
        return None

## Example usage
backing_store = {}
cache = WriteAroundCache(backing_store)
cache.set('user:3', {'name': 'Alice'})
print(cache.get('user:3'))  # Outputs: {'name': 'Alice'}
```
"""
    )
    print(output.content)
