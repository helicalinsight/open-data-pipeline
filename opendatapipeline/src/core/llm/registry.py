"""Provider registry.

Maps provider name strings to their builder callables.

To add a new provider:
  1. Create ``core/llm/providers/<name>.py`` with a ``build_<name>_llm(config)`` function.
  2. Import and register it below — that's it.
"""

from typing import Callable

from src.core.llm.config import LLMConfig

# Lazy imports inside callables are avoided to keep startup deterministic;
# however, the openai / anthropic builders import their SDK at module level
# inside *their own* files, so a missing ``pip install langchain-openai``
# will only raise when that specific provider is selected.
from src.core.llm.providers.ollama import build_ollama_llm
from src.core.llm.providers.openai import build_openai_llm
from src.core.llm.providers.anthropic import build_anthropic_llm
from src.core.llm.providers.gemini import build_gemini_llm
from src.core.llm.providers.mock import build_mock_llm

# Type alias for provider builder functions.
ProviderBuilder = Callable[[LLMConfig], object]

PROVIDER_REGISTRY: dict[str, ProviderBuilder] = {
    "ollama": build_ollama_llm,
    "openai": build_openai_llm,
    "anthropic": build_anthropic_llm,
    "google": build_gemini_llm,
    "mock": build_mock_llm,
    # Adding new providers is exactly one line here:
    # "groq":    build_groq_llm,
}
