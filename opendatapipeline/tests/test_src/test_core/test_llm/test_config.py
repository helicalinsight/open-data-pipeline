"""Tests for src.core.llm.config — LLMConfig resolution priority."""

import configparser
import os
from unittest.mock import patch

import pytest

from src.core.llm.config import LLMConfig


class TestLLMConfigDefaults:
    """When no env vars or INI config are present, defaults should apply."""

    @patch.dict(os.environ, {}, clear=True)
    def test_defaults_when_nothing_set(self):
        # Pass an empty ConfigParser so auto-discovery of local INI files
        # does not leak values into the test.
        empty_ini = configparser.ConfigParser()
        config = LLMConfig.from_env_and_config(ini_config=empty_ini)
        assert config.provider == "ollama"
        assert config.model == "openhermes"
        assert config.temperature == 0.0
        assert config.base_url is None
        assert config.api_key is None

    def test_dataclass_defaults_match(self):
        config = LLMConfig()
        assert config.provider == "ollama"
        assert config.model == "openhermes"


class TestLLMConfigIniResolution:
    """INI file values should fill in when env vars are absent."""

    @staticmethod
    def _make_ini(sections: dict) -> configparser.ConfigParser:
        parser = configparser.ConfigParser()
        for section, values in sections.items():
            parser.add_section(section)
            for key, val in values.items():
                parser.set(section, key, val)
        return parser

    @patch.dict(os.environ, {}, clear=True)
    def test_langchain_section_fallback(self):
        """When only [langchain] exists, values come from there."""
        ini = self._make_ini({
            "langchain": {
                "model": "llama3",
                "temperature": "0.5",
                "base_url": "http://my-ollama:11434",
            }
        })
        config = LLMConfig.from_env_and_config(ini_config=ini)
        assert config.provider == "ollama"  # default, not in ini
        assert config.model == "llama3"
        assert config.temperature == 0.5
        assert config.base_url == "http://my-ollama:11434"

    @patch.dict(os.environ, {}, clear=True)
    def test_llm_section_takes_priority_over_langchain(self):
        """[llm] section should win over [langchain] for overlapping keys."""
        ini = self._make_ini({
            "llm": {
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": "0.7",
            },
            "langchain": {
                "model": "old-model",
                "temperature": "0",
                "base_url": "http://old-url:11434",
            },
        })
        config = LLMConfig.from_env_and_config(ini_config=ini)
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.temperature == 0.7
        # base_url falls through to [langchain]
        assert config.base_url == "http://old-url:11434"


class TestLLMConfigEnvVarPriority:
    """Environment variables should always override INI values."""

    @staticmethod
    def _make_ini(sections: dict) -> configparser.ConfigParser:
        parser = configparser.ConfigParser()
        for section, values in sections.items():
            parser.add_section(section)
            for key, val in values.items():
                parser.set(section, key, val)
        return parser

    @patch.dict(os.environ, {
        "LLM_PROVIDER": "anthropic",
        "ANTHROPIC_MODEL": "claude-3-5-sonnet",
        "LLM_TEMPERATURE": "0.3",
        "ANTHROPIC_API_KEY": "sk-ant-test",
    }, clear=True)
    def test_env_vars_override_ini(self):
        ini = self._make_ini({
            "llm": {
                "provider": "ollama",
                "model": "ignored-model",
                "temperature": "0",
            }
        })
        config = LLMConfig.from_env_and_config(ini_config=ini)
        assert config.provider == "anthropic"
        assert config.model == "claude-3-5-sonnet"
        assert config.temperature == 0.3
        assert config.api_key == "sk-ant-test"

    @patch.dict(os.environ, {
        "LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": "sk-test-key",
    }, clear=True)
    def test_openai_api_key_resolved(self):
        config = LLMConfig.from_env_and_config(ini_config=None)
        assert config.provider == "openai"
        assert config.api_key == "sk-test-key"

    @patch.dict(os.environ, {
        "LLM_PROVIDER": "ollama",
    }, clear=True)
    def test_ollama_has_no_api_key(self):
        config = LLMConfig.from_env_and_config(ini_config=None)
        assert config.provider == "ollama"
        assert config.api_key is None

    @patch.dict(os.environ, {
        "LLM_PROVIDER": "google",
        "GOOGLE_API_KEY": "AIza-test-key",
    }, clear=True)
    def test_google_api_key_resolved(self):
        config = LLMConfig.from_env_and_config(ini_config=None)
        assert config.provider == "google"
        assert config.api_key == "AIza-test-key"

    @patch.dict(os.environ, {
        "LLM_TEMPERATURE": "not_a_number",
    }, clear=True)
    def test_invalid_temperature_falls_back_to_zero(self):
        config = LLMConfig.from_env_and_config(ini_config=None)
        assert config.temperature == 0.0


class TestLLMConfigImmutability:
    """LLMConfig should be a frozen dataclass."""

    def test_cannot_mutate_fields(self):
        config = LLMConfig()
        with pytest.raises(AttributeError):
            config.provider = "openai"  # type: ignore[misc]


class TestLLMConfigValidation:
    """LLMConfig.__post_init__ should catch invalid required params."""

    def test_empty_model_raises(self):
        with pytest.raises(ValueError, match="model must be a non-empty string"):
            LLMConfig(model="")

    def test_whitespace_model_raises(self):
        with pytest.raises(ValueError, match="model must be a non-empty string"):
            LLMConfig(model="   ")

    def test_empty_provider_raises(self):
        with pytest.raises(ValueError, match="provider must be a non-empty string"):
            LLMConfig(provider="")

    def test_temperature_too_high_raises(self):
        with pytest.raises(ValueError, match="between 0.0 and 2.0"):
            LLMConfig(temperature=3.0)

    def test_temperature_negative_raises(self):
        with pytest.raises(ValueError, match="between 0.0 and 2.0"):
            LLMConfig(temperature=-0.5)

    def test_valid_temperature_boundary(self):
        """Edge values 0.0 and 2.0 should be accepted."""
        config_low = LLMConfig(temperature=0.0)
        config_high = LLMConfig(temperature=2.0)
        assert config_low.temperature == 0.0
        assert config_high.temperature == 2.0


class TestLLMConfigMaxTokens:
    """Tests for max_tokens field — defaults, resolution, and validation."""

    @staticmethod
    def _make_ini(sections: dict) -> configparser.ConfigParser:
        parser = configparser.ConfigParser()
        for section, values in sections.items():
            parser.add_section(section)
            for key, val in values.items():
                parser.set(section, key, val)
        return parser

    @patch.dict(os.environ, {}, clear=True)
    def test_max_tokens_defaults_to_none(self):
        """When nothing is set, max_tokens should be None (provider default)."""
        config = LLMConfig.from_env_and_config(ini_config=configparser.ConfigParser())
        assert config.max_tokens is None

    @patch.dict(os.environ, {"LLM_MAX_TOKENS": "512"}, clear=True)
    def test_env_var_sets_max_tokens(self):
        """LLM_MAX_TOKENS env var should be resolved."""
        config = LLMConfig.from_env_and_config(ini_config=configparser.ConfigParser())
        assert config.max_tokens == 512

    @patch.dict(os.environ, {}, clear=True)
    def test_ini_llm_section_sets_max_tokens(self):
        """max_tokens from [llm] ini section should be picked up."""
        ini = self._make_ini({"llm": {"provider": "ollama", "model": "openhermes", "max_tokens": "1024"}})
        config = LLMConfig.from_env_and_config(ini_config=ini)
        assert config.max_tokens == 1024

    @patch.dict(os.environ, {"LLM_MAX_TOKENS": "2048"}, clear=True)
    def test_env_var_overrides_ini_max_tokens(self):
        """LLM_MAX_TOKENS env var must win over INI value."""
        ini = self._make_ini({"llm": {"provider": "ollama", "model": "openhermes", "max_tokens": "100"}})
        config = LLMConfig.from_env_and_config(ini_config=ini)
        assert config.max_tokens == 2048

    @patch.dict(os.environ, {"LLM_MAX_TOKENS": "not_a_number"}, clear=True)
    def test_invalid_env_var_falls_back_to_none(self):
        """A non-integer LLM_MAX_TOKENS should log a warning and default to None."""
        config = LLMConfig.from_env_and_config(ini_config=configparser.ConfigParser())
        assert config.max_tokens is None

    def test_max_tokens_zero_raises(self):
        """max_tokens=0 must be rejected (must be > 0)."""
        with pytest.raises(ValueError, match="max_tokens must be a positive integer"):
            LLMConfig(max_tokens=0)

    def test_max_tokens_negative_raises(self):
        """max_tokens=-1 must be rejected."""
        with pytest.raises(ValueError, match="max_tokens must be a positive integer"):
            LLMConfig(max_tokens=-1)

    def test_max_tokens_valid_positive_accepted(self):
        """Any positive integer should be accepted."""
        config = LLMConfig(max_tokens=1)
        assert config.max_tokens == 1
        config_large = LLMConfig(max_tokens=100_000)
        assert config_large.max_tokens == 100_000
