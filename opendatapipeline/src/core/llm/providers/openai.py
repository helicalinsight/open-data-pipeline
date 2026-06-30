"""OpenAI provider adapter.

Builds a ChatOpenAI instance from generic LLMConfig.
"""

from langchain_openai import ChatOpenAI

from src.core.llm.config import LLMConfig


def build_openai_llm(config: LLMConfig) -> ChatOpenAI:
    """Create a ChatOpenAI instance from the given config.

    :param config: Resolved LLM configuration.
    :type config: LLMConfig
    :return: A configured ChatOpenAI instance.
    :rtype: ChatOpenAI
    :raises ValueError: If no API key is available.
    """
    if not config.api_key:
        raise ValueError(
            "OpenAI provider requires an API key. "
            "Set the OPENAI_API_KEY environment variable or provide it in config."
        )
    kwargs: dict = {
        "model": config.model,
        "temperature": config.temperature,
        "api_key": config.api_key,
    }
    if config.max_tokens is not None:
        kwargs["max_tokens"] = config.max_tokens
    llm = ChatOpenAI(**kwargs)
    # All providers must return a BaseChatModel-compatible instance
    # supporting invoke(), stream(), ainvoke(), astream().
    return llm
