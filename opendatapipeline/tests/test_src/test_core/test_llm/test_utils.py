"""Tests for src.core.llm.utils — truncation detection helper."""

from unittest.mock import patch

from langchain_core.messages import AIMessage

from src.core.llm.utils import check_response_truncation

# Logger name used in utils.py
_LOGGER_PATCH_TARGET = "src.core.llm.utils.logger.warning"


def _make_response(metadata: dict) -> AIMessage:
    """Helper: build an AIMessage with the given response_metadata."""
    msg = AIMessage(content="some response")
    object.__setattr__(msg, "response_metadata", metadata)
    return msg


class TestCheckResponseTruncationDetected:
    """Each provider's truncation sentinel should return True and log a WARNING."""

    @patch(_LOGGER_PATCH_TARGET)
    def test_openai_length_truncation(self, mock_warning):
        response = _make_response({"finish_reason": "length"})
        result = check_response_truncation(
            response, provider="openai", model="gpt-4o", max_tokens=512
        )
        assert result is True
        mock_warning.assert_called_once()
        log_msg = mock_warning.call_args[0][0].lower()
        assert "truncated" in log_msg

    @patch(_LOGGER_PATCH_TARGET)
    def test_anthropic_max_tokens_truncation(self, mock_warning):
        response = _make_response({"stop_reason": "max_tokens"})
        result = check_response_truncation(
            response, provider="anthropic", model="claude-3-5-sonnet", max_tokens=1024
        )
        assert result is True
        mock_warning.assert_called_once()
        log_msg = mock_warning.call_args[0][0].lower()
        assert "truncated" in log_msg

    @patch(_LOGGER_PATCH_TARGET)
    def test_ollama_length_truncation(self, mock_warning):
        response = _make_response({"done_reason": "length"})
        result = check_response_truncation(
            response, provider="ollama", model="openhermes", max_tokens=256
        )
        assert result is True
        mock_warning.assert_called_once()
        log_msg = mock_warning.call_args[0][0].lower()
        assert "truncated" in log_msg

    @patch(_LOGGER_PATCH_TARGET)
    def test_google_max_tokens_truncation(self, mock_warning):
        response = _make_response({"finish_reason": "MAX_TOKENS"})
        result = check_response_truncation(
            response, provider="google", model="gemini-2.0-flash", max_tokens=2048
        )
        assert result is True
        mock_warning.assert_called_once()
        log_msg = mock_warning.call_args[0][0].lower()
        assert "truncated" in log_msg


class TestCheckResponseTruncationNotDetected:
    """Normal finish reasons should return False and emit no WARNING."""

    @patch(_LOGGER_PATCH_TARGET)
    def test_openai_stop_is_not_truncation(self, mock_warning):
        response = _make_response({"finish_reason": "stop"})
        result = check_response_truncation(response, provider="openai")
        assert result is False
        mock_warning.assert_not_called()

    @patch(_LOGGER_PATCH_TARGET)
    def test_anthropic_end_turn_is_not_truncation(self, mock_warning):
        response = _make_response({"stop_reason": "end_turn"})
        result = check_response_truncation(response, provider="anthropic")
        assert result is False
        mock_warning.assert_not_called()

    @patch(_LOGGER_PATCH_TARGET)
    def test_ollama_stop_is_not_truncation(self, mock_warning):
        response = _make_response({"done_reason": "stop"})
        result = check_response_truncation(response, provider="ollama")
        assert result is False
        mock_warning.assert_not_called()

    @patch(_LOGGER_PATCH_TARGET)
    def test_google_stop_is_not_truncation(self, mock_warning):
        response = _make_response({"finish_reason": "STOP"})
        result = check_response_truncation(response, provider="google")
        assert result is False
        mock_warning.assert_not_called()


class TestCheckResponseTruncationEdgeCases:
    """Edge cases: missing metadata, None values, unknown provider."""

    @patch(_LOGGER_PATCH_TARGET)
    def test_missing_response_metadata_returns_false(self, mock_warning):
        """A response with no response_metadata must not crash."""
        response = AIMessage(content="hello")
        result = check_response_truncation(response, provider="openai")
        assert result is False
        mock_warning.assert_not_called()

    @patch(_LOGGER_PATCH_TARGET)
    def test_empty_response_metadata_returns_false(self, mock_warning):
        response = _make_response({})
        result = check_response_truncation(response, provider="openai")
        assert result is False
        mock_warning.assert_not_called()

    @patch(_LOGGER_PATCH_TARGET)
    def test_unknown_provider_uses_default_check(self, mock_warning):
        """An unregistered provider falls back to checking finish_reason='length'."""
        response = _make_response({"finish_reason": "length"})
        result = check_response_truncation(response, provider="unknown_provider")
        assert result is True
        mock_warning.assert_called_once()

    @patch(_LOGGER_PATCH_TARGET)
    def test_max_tokens_none_in_log_message(self, mock_warning):
        """When max_tokens is None, the log should still emit 'provider_default'."""
        response = _make_response({"finish_reason": "length"})
        check_response_truncation(response, provider="openai", max_tokens=None)
        mock_warning.assert_called_once()
        args, _ = mock_warning.call_args
        # args[0] is the format string, args[1:] are the arguments
        # The third formatting argument corresponds to max_tokens
        assert args[3] == "provider_default"
