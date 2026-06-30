"""
Core datasource connector factory.

Provides the ``DataSourceConnector`` factory class that maps data source
type strings to their concrete ``DBConnection`` implementations using
lazy imports to avoid loading all dependencies at import time.
"""

import importlib
import logging
from typing import Any, Dict, Optional, Type

from .base import DBConnection
from .exceptions import DataSourceException

logger = logging.getLogger(__name__)


class DataSourceConnector:
    """
    Factory class that creates ``DBConnection`` instances by source type.

    The ``DEFAULT_MAPPING`` maps each supported data source type string to
    a tuple of ``(module_path, class_name)`` so that implementations are
    imported lazily — only when ``create()`` is called for that type.

    Usage::

        connector = DataSourceConnector()
        db = connector.create("postgres")          # Returns a DBConnection
        engine = db.get_engine(connection_details)  # SQLAlchemy Engine

    To extend with custom mappings::

        connector = DataSourceConnector()
        connector.register("my_db", "myapp.connectors.my_db", "MyDBConnection")
        db = connector.create("my_db")
    """

    # Mapping: source_type -> (module_path, class_name)
    # Module paths are relative to core.datasource.implementations
    DEFAULT_MAPPING: Dict[str, tuple] = {
        "astra": ("core.datasource.implementations.astra", "Astra"),
        "cassandra": ("core.datasource.implementations.cassandra", "Cassandra"),
        "firebird": ("core.datasource.implementations.sql_alchemy", "SqlAlchemy"),
        "mysql": ("core.datasource.implementations.sql_alchemy", "SqlAlchemy"),
        "postgres": ("core.datasource.implementations.sql_alchemy", "SqlAlchemy"),
        "redshift": ("core.datasource.implementations.redshift", "Redshift"),
        "snowflake": ("core.datasource.implementations.sql_alchemy", "SqlAlchemy"),
        "oracle": ("core.datasource.implementations.sql_alchemy", "SqlAlchemy"),
        "ms_sql_server": ("core.datasource.implementations.sql_alchemy", "SqlAlchemy"),
        "google_sheets": ("core.datasource.implementations.google_sheets", "GoogleSheets"),
        "s3": ("core.datasource.implementations.s3", "S3"),
        "couchbase": ("core.datasource.implementations.document_db", "UnifiedDocumentDB"),
        "databricks": ("core.datasource.implementations.sql_alchemy", "SqlAlchemy"),
    }

    def __init__(self) -> None:
        # Instance-level mapping allows per-instance customisation
        self._mapping: Dict[str, tuple] = dict(self.DEFAULT_MAPPING)
        # Cache of already-imported classes
        self._class_cache: Dict[str, Type[DBConnection]] = {}

    def register(self, source_type: str, module_path: str, class_name: str) -> None:
        """
        Register (or override) a source type mapping.

        Args:
            source_type: The data source type key (e.g. ``'postgres'``).
            module_path: Fully qualified Python module path.
            class_name: The class name within the module.
        """
        self._mapping[source_type] = (module_path, class_name)
        # Invalidate cache for this type
        self._class_cache.pop(source_type, None)

    def create(self, source_type: str) -> DBConnection:
        """
        Create and return a ``DBConnection`` instance for the given type.

        Uses lazy importing — the implementation module is only loaded
        when this method is first called for a given ``source_type``.

        Args:
            source_type: Data source type string (e.g. ``'postgres'``,
                ``'s3'``, ``'cassandra'``).

        Returns:
            An instance of the corresponding ``DBConnection`` subclass.

        Raises:
            DataSourceException: If the source type is not registered or
                the implementation cannot be loaded.
        """
        if source_type not in self._mapping:
            raise DataSourceException(
                f"Unsupported data source type: '{source_type}'. "
                f"Supported types: {sorted(self._mapping.keys())}"
            )

        # Return cached class if available
        if source_type not in self._class_cache:
            module_path, class_name = self._mapping[source_type]
            try:
                module = importlib.import_module(module_path)
                cls = getattr(module, class_name)
            except (ImportError, AttributeError) as e:
                raise DataSourceException(
                    f"Failed to load implementation for '{source_type}' "
                    f"({module_path}.{class_name}): {e}"
                ) from e
            self._class_cache[source_type] = cls

        try:
            return self._class_cache[source_type]()
        except Exception as e:
            logger.error(
                "Error creating connector for '%s': %s",
                source_type,
                str(e),
                exc_info=True,
            )
            raise DataSourceException(
                f"Error creating connector for '{source_type}': {e}"
            ) from e
