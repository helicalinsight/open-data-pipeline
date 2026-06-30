"""Conftest for core.llm tests.

These tests are fully isolated from the main application bootstrap (Flask,
MongoDB, Airflow) and only exercise the LLM abstraction layer.
"""

import os

import pytest


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch, tmp_path):
    """Ensure each test starts with a clean environment and no stale .env leaks.

    Sets AIRFLOW_HOME to a temp dir (required by the root conftest chain if
    it gets loaded) and clears any LLM-related env vars that could leak
    between tests.
    """
    monkeypatch.setenv("AIRFLOW_HOME", str(tmp_path))
    for var in (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_TEMPERATURE",
        "LLM_MAX_TOKENS",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_MODEL",
        "GOOGLE_API_KEY",
        "GOOGLE_MODEL",
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL",
        "APP_ENVIRONMENT",
    ):
        monkeypatch.delenv(var, raising=False)
