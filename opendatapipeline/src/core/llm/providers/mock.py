"""Mock provider adapter for testing.

Builds a FakeChatModel instance that returns deterministic responses,
allowing tests to exercise the full factory pipeline without network calls.
"""

from typing import Any, Iterator, List, Optional

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult

from src.core.llm.config import LLMConfig


class _FakeChatModel(BaseChatModel):
    """A fake chat model that returns a fixed response.

    Implements all members used by downstream consumers:
    - ``invoke()`` / ``ainvoke()``  (via ``_generate``)
    - ``stream()`` / ``astream()``  (via ``_stream``)
    - ``.content`` on the returned ``AIMessage``

    This avoids importing external test utilities and keeps the mock
    implementation fully in-tree.
    """

    response_text: str = "mock response"

    @property
    def _llm_type(self) -> str:
        return "fake-chat-model"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Synchronous generation — powers ``invoke()``."""
        message = AIMessage(content=self.response_text)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Streaming generation — powers ``stream()``.

        Yields the full response as a single chunk for simplicity.
        """
        chunk = ChatGenerationChunk(
            message=AIMessageChunk(content=self.response_text)
        )
        yield chunk


def build_mock_llm(config: LLMConfig) -> BaseChatModel:
    """Create a FakeChatModel for use in test environments.

    :param config: Resolved LLM configuration (largely ignored for mock).
    :type config: LLMConfig
    :return: A fake chat model that returns deterministic responses.
    :rtype: BaseChatModel
    """
    return _FakeChatModel(response_text="mock response")
