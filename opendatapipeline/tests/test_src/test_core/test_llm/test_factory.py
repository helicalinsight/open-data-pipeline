"""Tests for src.core.llm.factory — get_chat_model()."""

import os
from unittest.mock import patch, MagicMock

import pytest

from src.core.llm.config import LLMConfig
from src.core.llm.factory import get_chat_model


class TestGetChatModel:
    """Test the factory function with explicit configs."""

    def test_mock_provider_returns_fake_model(self):
        """The mock provider should always succeed without network calls."""
        config = LLMConfig(provider="mock")
        llm = get_chat_model(config)
        # Should be able to invoke without errors
        result = llm.invoke("Hello")
        assert result.content == "mock response"

    def test_unknown_provider_raises_value_error(self):
        config = LLMConfig(provider="nonexistent_provider")
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_chat_model(config)

    def test_unknown_provider_error_lists_supported(self):
        """Error message should list all supported providers."""
        config = LLMConfig(provider="bad")
        with pytest.raises(ValueError) as exc_info:
            get_chat_model(config)
        error_msg = str(exc_info.value)
        assert "anthropic" in error_msg
        assert "google" in error_msg
        assert "mock" in error_msg
        assert "ollama" in error_msg
        assert "openai" in error_msg

    @patch.dict(os.environ, {"LLM_PROVIDER": "mock"}, clear=True)
    def test_auto_resolve_config_from_env(self):
        """When config=None, the factory should resolve from env/ini/defaults."""
        llm = get_chat_model()
        result = llm.invoke("test")
        assert result.content == "mock response"


class TestGetChatModelProviderValidation:
    """Test that provider-specific validation works through the factory."""

    def test_openai_without_api_key_raises(self):
        config = LLMConfig(provider="openai", model="gpt-4o")
        with pytest.raises(ValueError, match="API key"):
            get_chat_model(config)

    def test_anthropic_without_api_key_raises(self):
        config = LLMConfig(provider="anthropic", model="claude-3-5-sonnet")
        with pytest.raises(ValueError, match="API key"):
            get_chat_model(config)

    def test_gemini_without_api_key_raises(self):
        config = LLMConfig(provider="google", model="gemini-2.0-flash")
        with pytest.raises(ValueError, match="API key"):
            get_chat_model(config)
