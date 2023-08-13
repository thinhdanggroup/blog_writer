import sys
from typing import Any, Optional
from uuid import UUID

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult


class StreamConsoleCallbackManager(BaseCallbackHandler):
    output = ""

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        sys.stdout.write(token)
        self.output += token

    def on_llm_end(
            self,
            response: LLMResult,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            **kwargs: Any,
    ) -> None:
        sys.stdout.write("\n\n")
        sys.stdout.write("========================================\n")

