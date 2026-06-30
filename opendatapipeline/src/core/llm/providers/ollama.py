"""Ollama provider adapter.

Builds a ChatOllama instance from generic LLMConfig.
"""

from langchain_ollama import ChatOllama

from src.core.llm.config import LLMConfig


def build_ollama_llm(config: LLMConfig) -> ChatOllama:
    """Create a ChatOllama instance from the given config.

    :param config: Resolved LLM configuration.
    :type config: LLMConfig
    :return: A configured ChatOllama instance.
    :rtype: ChatOllama
    """
    kwargs: dict = {
        "model": config.model,
        "temperature": config.temperature,
    }
    if config.base_url:
        kwargs["base_url"] = config.base_url
    # Ollama uses `num_predict` instead of `max_tokens`.
    # The adapter translates the generic LLMConfig field transparently so
    # callers always set LLM_MAX_TOKENS / config.max_tokens regardless of provider.
    if config.max_tokens is not None:
        kwargs["num_predict"] = config.max_tokens
    # All providers must return a BaseChatModel-compatible instance
    # supporting invoke(), stream(), ainvoke(), astream().
    # Required params (model, temperature) are validated by LLMConfig.__post_init__.
    return ChatOllama(**kwargs)
