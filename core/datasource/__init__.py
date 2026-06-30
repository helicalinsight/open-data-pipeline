"""
Core datasource module.

Provides the shared data source connection abstraction used by
``opendatapipeline``, ``dlt_server_app``, and other applications.
"""

from .base import DBConnection
from .connector import DataSourceConnector
from .exceptions import DataSourceException

__all__ = ["DBConnection", "DataSourceConnector", "DataSourceException"]
