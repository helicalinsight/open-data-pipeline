"""Google Gemini provider adapter.

Builds a ChatGoogleGenerativeAI instance from generic LLMConfig.

Requires:
    pip install langchain-google-genai

API key:
    Set the ``GOOGLE_API_KEY`` environment variable, or pass it via config.
    Keys can be obtained from https://aistudio.google.com/app/apikey.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.llm.config import LLMConfig


def build_gemini_llm(config: LLMConfig) -> ChatGoogleGenerativeAI:
    """Create a ChatGoogleGenerativeAI instance from the given config.

    :param config: Resolved LLM configuration.
    :type config: LLMConfig
    :return: A configured ChatGoogleGenerativeAI instance.
    :rtype: ChatGoogleGenerativeAI
    :raises ValueError: If no API key is available.
    """
    if not config.api_key:
        raise ValueError(
            "Google Gemini provider requires an API key. "
            "Set the GOOGLE_API_KEY environment variable or provide it in config."
        )
    kwargs: dict = {
        "model": config.model,
        "temperature": config.temperature,
        "google_api_key": config.api_key,
    }
    if config.max_tokens is not None:
        # Must be set at constructor time for Gemini; per-invoke setting is unreliable.
        kwargs["max_tokens"] = config.max_tokens
    llm = ChatGoogleGenerativeAI(**kwargs, **config.extra)
    # All providers must return a BaseChatModel-compatible instance
    # supporting invoke(), stream(), ainvoke(), astream().
    return llm
