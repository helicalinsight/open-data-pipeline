"""LLM response utilities — truncation detection and structured logging.

This module provides helpers for inspecting LLM responses *after* they are
returned by the model.  The primary use-case is detecting when a response was
truncated because the configured ``max_tokens`` limit was reached, and emitting
a structured WARNING log so developers/operators know to adjust the setting.

Each provider encodes the truncation signal differently in
``AIMessage.response_metadata``.  The mapping below normalises that into a
single boolean check.

Usage (internal — called automatically by the factory wrapper)::

    from src.core.llm.utils import check_response_truncation

    truncated = check_response_truncation(
        response, provider="openai", model="gpt-4o", max_tokens=512
    )
"""

import logging
from typing import Optional

from langchain_core.messages import AIMessage

logger = logging.getLogger(__name__)

# Maps provider name → (metadata_key, truncation_sentinel_value).
# The sentinel is the value that indicates the model stopped because it hit
# the token limit rather than finishing naturally.
_TRUNCATION_SIGNALS: dict[str, tuple[str, str]] = {
    "openai":    ("finish_reason", "length"),
    "anthropic": ("stop_reason",   "max_tokens"),
    "ollama":    ("done_reason",   "length"),
    "google":    ("finish_reason", "MAX_TOKENS"),
}


def check_response_truncation(
    response: AIMessage,
    provider: str,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> bool:
    """Inspect ``response_metadata`` and emit a WARNING log if the response was
    truncated due to the ``max_tokens`` (or equivalent) limit being reached.

    The response itself is **not** modified; this function is purely
    observational.  The factory calls this automatically on every
    ``invoke()``/``ainvoke()`` so callers do not need to check manually.

    :param response: The ``AIMessage`` returned by the model.
    :param provider: The provider string (e.g. ``"openai"``, ``"anthropic"``).
    :param model: The model name, used for the log message only.
    :param max_tokens: The configured limit, used for the log message only.
    :return: ``True`` if the response was truncated, ``False`` otherwise.
    """
    # Gracefully handle providers not in the mapping (e.g. future ones).
    meta_key, truncation_value = _TRUNCATION_SIGNALS.get(
        provider, ("finish_reason", "length")
    )

    metadata: dict = getattr(response, "response_metadata", None) or {}
    actual_value = metadata.get(meta_key, "")

    if actual_value == truncation_value:
        logger.warning(
            "LLM response was truncated — the max_tokens limit was reached. "
            "provider=%r  model=%r  max_tokens=%s  finish_signal=%r. "
            "To receive a complete response, increase LLM_MAX_TOKENS (env var) "
            "or set 'max_tokens' in the [llm] section of your config file.",
            provider,
            model,
            max_tokens if max_tokens is not None else "provider_default",
            actual_value,
        )
        return True

    return False
