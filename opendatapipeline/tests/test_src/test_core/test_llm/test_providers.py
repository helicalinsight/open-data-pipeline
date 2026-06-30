"""Tests for individual provider adapters in src.core.llm.providers."""

from unittest.mock import patch

import pytest

from src.core.llm.config import LLMConfig


class TestMockProvider:
    """The mock provider should always work without external dependencies."""

    def test_build_mock_llm_returns_callable_model(self):
        from src.core.llm.providers.mock import build_mock_llm

        config = LLMConfig(provider="mock")
        llm = build_mock_llm(config)
        result = llm.invoke("anything")
        assert result.content == "mock response"

    def test_mock_llm_supports_streaming(self):
        from src.core.llm.providers.mock import build_mock_llm

        config = LLMConfig(provider="mock")
        llm = build_mock_llm(config)
        chunks = list(llm.stream("anything"))
        content = "".join(c.content for c in chunks)
        assert content == "mock response"

    def test_mock_llm_type(self):
        from src.core.llm.providers.mock import build_mock_llm

        config = LLMConfig(provider="mock")
        llm = build_mock_llm(config)
        assert llm._llm_type == "fake-chat-model"


class TestOllamaProvider:
    """Ollama provider adapter tests — constructor args validation."""

    @patch("src.core.llm.providers.ollama.ChatOllama")
    def test_build_ollama_passes_correct_args(self, mock_chat_ollama):
        from src.core.llm.providers.ollama import build_ollama_llm

        config = LLMConfig(
            provider="ollama",
            model="llama3",
            temperature=0.5,
            base_url="http://localhost:11434",
        )
        build_ollama_llm(config)
        call_kwargs = mock_chat_ollama.call_args[1]
        assert call_kwargs["model"] == "llama3"
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["base_url"] == "http://localhost:11434"
        assert "num_predict" not in call_kwargs  # max_tokens not set

    @patch("src.core.llm.providers.ollama.ChatOllama")
    def test_build_ollama_omits_base_url_when_none(self, mock_chat_ollama):
        from src.core.llm.providers.ollama import build_ollama_llm

        config = LLMConfig(provider="ollama", model="openhermes", base_url=None)
        build_ollama_llm(config)
        call_kwargs = mock_chat_ollama.call_args[1]
        assert "base_url" not in call_kwargs

    @patch("src.core.llm.providers.ollama.ChatOllama")
    def test_build_ollama_passes_num_predict_when_max_tokens_set(self, mock_chat_ollama):
        """Ollama uses num_predict; the adapter must translate max_tokens → num_predict."""
        from src.core.llm.providers.ollama import build_ollama_llm

        config = LLMConfig(provider="ollama", model="openhermes", max_tokens=512)
        build_ollama_llm(config)
        call_kwargs = mock_chat_ollama.call_args[1]
        assert call_kwargs["num_predict"] == 512
        assert "max_tokens" not in call_kwargs  # should NOT appear for Ollama

    @patch("src.core.llm.providers.ollama.ChatOllama")
    def test_build_ollama_omits_num_predict_when_max_tokens_none(self, mock_chat_ollama):
        from src.core.llm.providers.ollama import build_ollama_llm

        config = LLMConfig(provider="ollama", model="openhermes", max_tokens=None)
        build_ollama_llm(config)
        call_kwargs = mock_chat_ollama.call_args[1]
        assert "num_predict" not in call_kwargs


class TestOpenAIProvider:
    """OpenAI provider adapter tests."""

    def test_build_openai_requires_api_key(self):
        from src.core.llm.providers.openai import build_openai_llm

        config = LLMConfig(provider="openai", model="gpt-4o", api_key=None)
        with pytest.raises(ValueError, match="API key"):
            build_openai_llm(config)

    @patch("src.core.llm.providers.openai.ChatOpenAI")
    def test_build_openai_passes_correct_args(self, mock_chat_openai):
        from src.core.llm.providers.openai import build_openai_llm

        config = LLMConfig(
            provider="openai",
            model="gpt-4o",
            temperature=0.7,
            api_key="sk-test",
        )
        build_openai_llm(config)
        call_kwargs = mock_chat_openai.call_args[1]
        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["api_key"] == "sk-test"
        assert "max_tokens" not in call_kwargs  # max_tokens not set

    @patch("src.core.llm.providers.openai.ChatOpenAI")
    def test_build_openai_passes_max_tokens_when_set(self, mock_chat_openai):
        from src.core.llm.providers.openai import build_openai_llm

        config = LLMConfig(provider="openai", model="gpt-4o", api_key="sk-test", max_tokens=1024)
        build_openai_llm(config)
        call_kwargs = mock_chat_openai.call_args[1]
        assert call_kwargs["max_tokens"] == 1024

    @patch("src.core.llm.providers.openai.ChatOpenAI")
    def test_build_openai_omits_max_tokens_when_none(self, mock_chat_openai):
        from src.core.llm.providers.openai import build_openai_llm

        config = LLMConfig(provider="openai", model="gpt-4o", api_key="sk-test", max_tokens=None)
        build_openai_llm(config)
        call_kwargs = mock_chat_openai.call_args[1]
        assert "max_tokens" not in call_kwargs


class TestAnthropicProvider:
    """Anthropic provider adapter tests."""

    def test_build_anthropic_requires_api_key(self):
        from src.core.llm.providers.anthropic import build_anthropic_llm

        config = LLMConfig(provider="anthropic", model="claude-3-5-sonnet", api_key=None)
        with pytest.raises(ValueError, match="API key"):
            build_anthropic_llm(config)

    @patch("src.core.llm.providers.anthropic.ChatAnthropic")
    def test_build_anthropic_passes_correct_args(self, mock_chat_anthropic):
        from src.core.llm.providers.anthropic import build_anthropic_llm

        config = LLMConfig(
            provider="anthropic",
            model="claude-3-5-sonnet",
            temperature=0.3,
            api_key="sk-ant-test",
        )
        build_anthropic_llm(config)
        call_kwargs = mock_chat_anthropic.call_args[1]
        assert call_kwargs["model"] == "claude-3-5-sonnet"
        assert call_kwargs["temperature"] == 0.3
        assert call_kwargs["api_key"] == "sk-ant-test"
        assert "max_tokens" not in call_kwargs  # max_tokens not set

    @patch("src.core.llm.providers.anthropic.ChatAnthropic")
    def test_build_anthropic_passes_max_tokens_when_set(self, mock_chat_anthropic):
        from src.core.llm.providers.anthropic import build_anthropic_llm

        config = LLMConfig(provider="anthropic", model="claude-3-5-sonnet", api_key="sk-ant-test", max_tokens=2048)
        build_anthropic_llm(config)
        call_kwargs = mock_chat_anthropic.call_args[1]
        assert call_kwargs["max_tokens"] == 2048

    @patch("src.core.llm.providers.anthropic.ChatAnthropic")
    def test_build_anthropic_omits_max_tokens_when_none(self, mock_chat_anthropic):
        from src.core.llm.providers.anthropic import build_anthropic_llm

        config = LLMConfig(provider="anthropic", model="claude-3-5-sonnet", api_key="sk-ant-test", max_tokens=None)
        build_anthropic_llm(config)
        call_kwargs = mock_chat_anthropic.call_args[1]
        assert "max_tokens" not in call_kwargs

class TestGeminiProvider:
    """Google Gemini provider adapter tests."""

    def test_build_gemini_requires_api_key(self):
        from src.core.llm.providers.gemini import build_gemini_llm

        config = LLMConfig(provider="google", model="gemini-2.0-flash", api_key=None)
        with pytest.raises(ValueError, match="API key"):
            build_gemini_llm(config)

    @patch("src.core.llm.providers.gemini.ChatGoogleGenerativeAI")
    def test_build_gemini_passes_correct_args(self, mock_chat_google):
        from src.core.llm.providers.gemini import build_gemini_llm

        config = LLMConfig(
            provider="google",
            model="gemini-2.0-flash",
            temperature=0.4,
            api_key="AIza-test-key",
        )
        build_gemini_llm(config)
        call_kwargs = mock_chat_google.call_args[1]
        assert call_kwargs["model"] == "gemini-2.0-flash"
        assert call_kwargs["temperature"] == 0.4
        assert call_kwargs["google_api_key"] == "AIza-test-key"
        assert "max_tokens" not in call_kwargs  # max_tokens not set

    @patch("src.core.llm.providers.gemini.ChatGoogleGenerativeAI")
    def test_build_gemini_passes_max_tokens_when_set(self, mock_chat_google):
        from src.core.llm.providers.gemini import build_gemini_llm

        config = LLMConfig(provider="google", model="gemini-2.0-flash", api_key="AIza-test-key", max_tokens=4096)
        build_gemini_llm(config)
        call_kwargs = mock_chat_google.call_args[1]
        assert call_kwargs["max_tokens"] == 4096

    @patch("src.core.llm.providers.gemini.ChatGoogleGenerativeAI")
    def test_build_gemini_omits_max_tokens_when_none(self, mock_chat_google):
        from src.core.llm.providers.gemini import build_gemini_llm

        config = LLMConfig(provider="google", model="gemini-2.0-flash", api_key="AIza-test-key", max_tokens=None)
        build_gemini_llm(config)
        call_kwargs = mock_chat_google.call_args[1]
        assert "max_tokens" not in call_kwargs

    @patch("src.core.llm.providers.gemini.ChatGoogleGenerativeAI")
    def test_build_gemini_passes_extra_kwargs(self, mock_chat_google):
        from src.core.llm.providers.gemini import build_gemini_llm

        config = LLMConfig(
            provider="google",
            model="gemini-2.0-flash",
            api_key="AIza-test-key",
            extra={"max_output_tokens": 1024},
        )
        build_gemini_llm(config)
        call_kwargs = mock_chat_google.call_args[1]
        assert call_kwargs["max_output_tokens"] == 1024


class TestProviderRegistryCompleteness:
    """Verify the registry maps all expected providers."""

    def test_all_expected_providers_registered(self):
        from src.core.llm.registry import PROVIDER_REGISTRY

        expected = {"ollama", "openai", "anthropic", "google", "mock"}
        assert set(PROVIDER_REGISTRY.keys()) == expected

    def test_all_registry_values_are_callable(self):
        from src.core.llm.registry import PROVIDER_REGISTRY

        for name, builder in PROVIDER_REGISTRY.items():
            assert callable(builder), f"Registry entry '{name}' is not callable"
