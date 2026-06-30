"""LLM factory — the single entry point for all LLM creation.

Consumers should **never** import provider classes directly.  Instead::

    from src.core.llm import get_chat_model

    llm = get_chat_model()            # uses env/ini/defaults
    llm = get_chat_model(my_config)   # explicit config override

The returned object is a standard ``BaseChatModel`` and is fully compatible
with ``invoke()`` / ``stream()`` / ``ainvoke()`` / ``astream()``.

Truncation detection
--------------------
When ``max_tokens`` is configured (or even when it isn't), the factory wraps
``invoke()`` and ``ainvoke()`` to automatically emit a ``WARNING`` log if the
provider signals that the response was truncated.  This is completely
transparent to callers — the same ``AIMessage`` object is returned, unmodified.

Note: ``stream()`` / ``astream()`` are *not* wrapped because the truncation
signal is only available on the final ``AIMessage``, not on individual chunks.
Callers that use streaming and care about truncation should inspect the last
chunk's ``response_metadata`` directly, or collect the full response first.
"""

import logging
from typing import Any, Iterator, List, Optional

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatResult

from src.core.llm.config import LLMConfig
from src.core.llm.registry import PROVIDER_REGISTRY
from src.core.llm.utils import check_response_truncation

logger = logging.getLogger(__name__)


class _TruncationAwareChatModel(BaseChatModel):
    """A thin, transparent wrapper around any ``BaseChatModel``.

    Delegates all behaviour to the wrapped model.  Overrides ``invoke()``
    and ``ainvoke()`` to call :func:`check_response_truncation` after every
    call, emitting a ``WARNING`` log if the response was cut short.

    Consumers receive exactly the same ``AIMessage`` they would get from the
    inner model — the wrapper is purely observational.
    """

    # Pydantic fields for the wrapper's own state.
    # We store the config so we can pass provider/model/max_tokens to the
    # truncation checker without threading them through every call site.
    _inner: Any  # BaseChatModel (typed as Any to avoid Pydantic recursion)
    _llm_config: Any  # LLMConfig

    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, inner: BaseChatModel, config: LLMConfig, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Use object.__setattr__ because BaseChatModel is a Pydantic model
        # and these are private/non-field attributes.
        object.__setattr__(self, "_inner", inner)
        object.__setattr__(self, "_llm_config", config)

    # ------------------------------------------------------------------
    # Required BaseChatModel abstract method
    # ------------------------------------------------------------------

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Delegate to the inner model's ``_generate``."""
        return self._inner._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

    @property
    def _llm_type(self) -> str:
        return getattr(self._inner, "_llm_type", "truncation-aware-wrapper")

    # ------------------------------------------------------------------
    # Wrap invoke / ainvoke for truncation detection
    # ------------------------------------------------------------------

    def invoke(self, input: Any, **kwargs: Any) -> AIMessage:  # type: ignore[override]
        """Invoke the inner model and check for truncation."""
        response = self._inner.invoke(input, **kwargs)
        cfg: LLMConfig = self._llm_config
        if isinstance(response, AIMessage):
            check_response_truncation(
                response,
                provider=cfg.provider,
                model=cfg.model,
                max_tokens=cfg.max_tokens,
            )
        return response

    async def ainvoke(self, input: Any, **kwargs: Any) -> AIMessage:  # type: ignore[override]
        """Async-invoke the inner model and check for truncation."""
        response = await self._inner.ainvoke(input, **kwargs)
        cfg: LLMConfig = self._llm_config
        if isinstance(response, AIMessage):
            check_response_truncation(
                response,
                provider=cfg.provider,
                model=cfg.model,
                max_tokens=cfg.max_tokens,
            )
        return response

    # ------------------------------------------------------------------
    # Pass-through stream / astream unchanged (truncation not checkable
    # on individual chunks; callers that need it should inspect the last
    # chunk's response_metadata directly).
    # ------------------------------------------------------------------

    def stream(self, input: Any, **kwargs: Any) -> Iterator[Any]:  # type: ignore[override]
        return self._inner.stream(input, **kwargs)

    async def astream(self, input: Any, **kwargs: Any):  # type: ignore[override]
        async for chunk in self._inner.astream(input, **kwargs):
            yield chunk

    # ------------------------------------------------------------------
    # Delegate everything else to the inner model transparently.
    # ------------------------------------------------------------------

    def __getattr__(self, name: str) -> Any:
        # Fallback: delegate attribute access to the inner model so that
        # provider-specific attributes (e.g. .model_name, .client) still work.
        try:
            return object.__getattribute__(self, "_inner").__getattribute__(name)
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )


def get_chat_model(config: LLMConfig | None = None) -> BaseChatModel:
    """Build and return a ``BaseChatModel`` for the configured provider.

    The returned model transparently wraps ``invoke()``/``ainvoke()`` to emit
    a ``WARNING`` log whenever the provider signals that the response was
    truncated due to the ``max_tokens`` limit.

    :param config: An explicit LLM configuration.  When ``None``, the config
        is resolved automatically from environment variables and INI files.
    :type config: LLMConfig | None
    :return: A LangChain-compatible chat model ready for ``invoke()`` / ``stream()``.
    :rtype: BaseChatModel
    :raises ValueError: If the provider name is not registered.
    """
    if config is None:
        config = LLMConfig.from_env_and_config()

    builder = PROVIDER_REGISTRY.get(config.provider)
    if builder is None:
        raise ValueError(
            f"Unknown LLM provider: '{config.provider}'. "
            f"Supported providers: {sorted(PROVIDER_REGISTRY)}"
        )

    logger.info(
        "Building LLM: provider=%s, model=%s, temperature=%s, max_tokens=%s",
        config.provider,
        config.model,
        config.temperature,
        config.max_tokens if config.max_tokens is not None else "provider_default",
    )
    llm = builder(config)

    # Runtime type check: ensure all providers return a BaseChatModel so
    # downstream calls to invoke(), stream(), ainvoke(), astream() will work.
    if not isinstance(llm, BaseChatModel):
        raise TypeError(
            f"Provider '{config.provider}' returned {type(llm).__name__}, "
            f"expected a BaseChatModel subclass. This would break downstream "
            f"calls to invoke()/stream()."
        )

    # Wrap with the truncation-aware proxy so every invoke/ainvoke call
    # automatically emits a WARNING if the response was cut short.
    return _TruncationAwareChatModel(inner=llm, config=config)
