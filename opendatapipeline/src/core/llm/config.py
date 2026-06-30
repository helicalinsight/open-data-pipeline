"""LLM configuration resolver.

Resolves LLM settings with the following priority order (12-factor style):
  1. Environment variables  (highest priority)
  2. ``[llm]`` section in the active ``.ini`` config file
  3. ``[langchain]`` section in the active ``.ini`` config file  (backward-compat)
  4. Hard-coded defaults    (lowest priority)

The ``.env`` file in the ``opendatapipeline/`` directory is loaded automatically
via ``python-dotenv`` so that local developers can set secrets there.
"""

import configparser
import logging
import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load the .env file from the opendatapipeline directory.
# ``find_dotenv`` would also work, but explicit path is safer.
_ASKONDATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
)
_DOTENV_PATH = os.path.join(_ASKONDATA_DIR, ".env")
load_dotenv(_DOTENV_PATH, override=False)


def _resolve_ini_config() -> Optional[configparser.ConfigParser]:
    """Return the active ``config/config-*.ini`` ConfigParser, or None."""
    config_dir = os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        os.pardir,
        "configurations",
        "config",
    )
    config_dir = os.path.abspath(config_dir)

    env = os.getenv("APP_ENVIRONMENT", "").lower()
    if env == "prod":
        filename = "config-prod.ini"
    elif env == "dev":
        filename = "config-dev.ini"
    elif env == "test":
        filename = "config-test.ini"
    else:
        filename = "config-local.ini"

    config_path = os.path.join(config_dir, filename)
    if not os.path.isfile(config_path):
        logger.debug("INI config file not found at %s", config_path)
        return None

    parser = configparser.ConfigParser()
    parser.read(config_path)
    return parser


# ---------------------------------------------------------------------------
# Provider ↔ environment variable mappings for API keys
# ---------------------------------------------------------------------------
_PROVIDER_API_KEY_ENV_VARS: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
}


@dataclass(frozen=True)
class LLMConfig:
    """Immutable value object holding all parameters needed to construct an LLM.

    Use :meth:`from_env_and_config` to build an instance with automatic
    resolution of environment variables and INI configuration files.
    """

    provider: str = "ollama"
    model: str = "openhermes"
    temperature: float = 0.0
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    # Maximum number of tokens the model may generate in a single response.
    # None means use the provider's own default (no explicit limit imposed).
    # Controls output cost; env var: LLM_MAX_TOKENS; ini key: max_tokens.
    max_tokens: Optional[int] = None
    # Arbitrary extra kwargs passed through to the provider builder.
    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate required configuration parameters."""
        if not self.provider or not self.provider.strip():
            raise ValueError("LLMConfig.provider must be a non-empty string.")
        if not self.model or not self.model.strip():
            raise ValueError(
                "LLMConfig.model must be a non-empty string. "
                "Set LLM_MODEL or OLLAMA_MODEL env var, or 'model' in your INI config."
            )
        if not isinstance(self.temperature, (int, float)):
            raise ValueError("LLMConfig.temperature must be a number.")
        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError(
                f"LLMConfig.temperature must be between 0.0 and 2.0, got {self.temperature}."
            )
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError(
                f"LLMConfig.max_tokens must be a positive integer, got {self.max_tokens}. "
                "Set LLM_MAX_TOKENS to a value > 0, or leave it unset to use the provider default."
            )

    @classmethod
    def from_env_and_config(
        cls,
        ini_config: Optional[configparser.ConfigParser] = None,
        extra: Optional[dict] = None,
    ) -> "LLMConfig":
        """Resolve configuration with priority: env vars > [llm] ini > [langchain] ini > defaults.

        :param ini_config: An already-loaded ConfigParser. If ``None``, the
            resolver will attempt to locate and load the active INI file
            automatically.
        :type ini_config: Optional[configparser.ConfigParser]
        :return: A fully-resolved LLMConfig instance.
        :rtype: LLMConfig
        """
        if ini_config is None:
            ini_config = _resolve_ini_config()

        # --- Step 1: Read INI fallback values ---------------------------------
        ini_provider: Optional[str] = None
        ini_model: Optional[str] = None
        ini_temperature: Optional[str] = None
        ini_base_url: Optional[str] = None
        ini_max_tokens: Optional[str] = None

        if ini_config is not None:
            # Prefer [llm] section, then fall back to [langchain]
            for section in ("llm", "langchain"):
                if ini_config.has_section(section):
                    ini_provider = ini_provider or ini_config.get(section, "provider", fallback=None)
                    ini_model = ini_model or ini_config.get(section, "model", fallback=None)
                    ini_temperature = ini_temperature or ini_config.get(section, "temperature", fallback=None)
                    ini_base_url = ini_base_url or ini_config.get(section, "base_url", fallback=None)
                    ini_max_tokens = ini_max_tokens or ini_config.get(section, "max_tokens", fallback=None)

        # --- Step 2: Resolve with env var priority ----------------------------
        provider_env = os.getenv("LLM_PROVIDER")
        provider = (provider_env if provider_env else (ini_provider or "ollama")).lower()
        
        model_env = os.getenv(f"{provider.upper()}_MODEL") or os.getenv("LLM_MODEL")
        model = model_env if model_env else (ini_model or "openhermes")
        try:
            temperature = float(
                os.getenv("LLM_TEMPERATURE", ini_temperature or "0")
            )
        except (ValueError, TypeError):
            temperature = 0.0

        base_url = os.getenv("OLLAMA_BASE_URL", ini_base_url)

        # --- Step 3: Resolve API key (provider-specific env var) ---------------
        api_key_env = _PROVIDER_API_KEY_ENV_VARS.get(provider)
        api_key = os.getenv(api_key_env) if api_key_env else None

        # --- Step 4: Resolve max_tokens (env var > ini > None) -----------------
        raw_max_tokens = os.getenv("LLM_MAX_TOKENS", ini_max_tokens)
        max_tokens: Optional[int] = None
        if raw_max_tokens is not None:
            try:
                max_tokens = int(raw_max_tokens)
            except (ValueError, TypeError):
                logger.warning(
                    "Invalid LLM_MAX_TOKENS value %r — ignoring, using provider default.",
                    raw_max_tokens,
                )

        return cls(
            provider=provider,
            model=model,
            temperature=temperature,
            base_url=base_url,
            api_key=api_key,
            max_tokens=max_tokens,
            extra=extra or {},
        )
