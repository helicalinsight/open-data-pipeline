"""Backward-compatible DatabaseConnector that delegates to core.datasource."""
import logging

from core.datasource.connector import DataSourceConnector

logger = logging.getLogger(__name__)

_connector = DataSourceConnector()


class DatabaseConnector:
    """Thin wrapper that delegates to :class:`core.datasource.connector.DataSourceConnector`."""

    collection_mapping = _connector._mapping  # expose for introspection

    @staticmethod
    def create_object(collection):
        try:
            return _connector.create(collection)
        except Exception as e:  # pragma: no cover
            logger.error("error while creating object %s", str(e), exc_info=True)
            return None
