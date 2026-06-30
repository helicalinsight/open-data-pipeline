"""Anthropic provider adapter.

Builds a ChatAnthropic instance from generic LLMConfig.
"""

from langchain_anthropic import ChatAnthropic

from src.core.llm.config import LLMConfig


def build_anthropic_llm(config: LLMConfig) -> ChatAnthropic:
    """Create a ChatAnthropic instance from the given config.

    :param config: Resolved LLM configuration.
    :type config: LLMConfig
    :return: A configured ChatAnthropic instance.
    :rtype: ChatAnthropic
    :raises ValueError: If no API key is available.
    """
    if not config.api_key:
        raise ValueError(
            "Anthropic provider requires an API key. "
            "Set the ANTHROPIC_API_KEY environment variable or provide it in config."
        )
    kwargs: dict = {
        "model": config.model,
        "temperature": config.temperature,
        "api_key": config.api_key,
    }
    if config.max_tokens is not None:
        kwargs["max_tokens"] = config.max_tokens
    llm = ChatAnthropic(**kwargs)
    # All providers must return a BaseChatModel-compatible instance
    # supporting invoke(), stream(), ainvoke(), astream().
    return llm
