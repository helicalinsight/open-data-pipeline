"""Public API for the LLM abstraction layer.

Usage::

    from src.core.llm import get_chat_model, LLMConfig

    # Auto-resolve from env / ini / defaults:
    llm = get_chat_model()

    # Explicit configuration:
    config = LLMConfig(provider="openai", model="gpt-4o", api_key="sk-...")
    llm = get_chat_model(config)

Truncation detection is **automatic** — every ``invoke()``/``ainvoke()`` call
will emit a ``WARNING`` log if the provider signals the response was cut short
due to the ``max_tokens`` limit.  No extra code is needed in callers.

Control max_tokens via:
  - ``LLM_MAX_TOKENS`` environment variable
  - ``max_tokens`` key in the ``[llm]`` section of your ``.ini`` config file
"""

from src.core.llm.config import LLMConfig
from src.core.llm.factory import get_chat_model

__all__ = ["get_chat_model", "LLMConfig"]
