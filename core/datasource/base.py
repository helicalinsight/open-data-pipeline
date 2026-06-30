"""
Core datasource base module.

Defines the DBConnection abstract base class that all database connector
implementations must inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DBConnection(ABC):
    """
    Abstract base class for all database connections.

    Subclasses must implement the five abstract methods for connecting,
    testing, fetching data, and retrieving metadata/columns.

    Additionally, RDBMS-based connectors should override
    ``get_connection_string()`` and ``get_engine()`` to support
    SQLAlchemy-based workflows (e.g. dlt pipelines).
    """

    @abstractmethod
    def connect(self, connection_details: Dict[str, Any], engine: Optional[Any] = None) -> Any:
        """
        Establish a connection to the data source.

        Args:
            connection_details: Dictionary containing connection parameters
                (host, port, username, password, database, etc.).
            engine: Optional pre-existing engine/connection object to reuse.

        Returns:
            A connection object specific to the data source.
        """
        pass

    @abstractmethod
    def test_connection(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[Any] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """
        Test whether a connection to the data source can be established.

        Args:
            connection_details: Dictionary containing connection parameters.
            engine: Optional pre-existing engine to test against.
            connection: Optional pre-existing connection to test.

        Returns:
            A result indicating connection success/failure.
        """
        pass

    @abstractmethod
    def fetch_data(
        self,
        connection_details: Dict[str, Any],
        catalog: str,
        columns: List[str] = [],
        engine: Optional[Any] = None,
        connection: Optional[Any] = None,
        num_rows: int = 100,
    ) -> Any:
        """
        Fetch data from the data source.

        Args:
            connection_details: Dictionary containing connection parameters.
            catalog: The table/catalog name to fetch data from.
            columns: List of column names to select; empty means all columns.
            engine: Optional pre-existing engine to use.
            connection: Optional pre-existing connection to use.
            num_rows: Maximum number of rows to return.

        Returns:
            The fetched data (typically a pandas DataFrame).
        """
        pass

    @abstractmethod
    def get_metadata(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[Any] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """
        Retrieve metadata (schemas, tables, etc.) from the data source.

        Args:
            connection_details: Dictionary containing connection parameters.
            engine: Optional pre-existing engine to use.
            connection: Optional pre-existing connection to use.

        Returns:
            Metadata structure describing available schemas/tables.
        """
        pass

    @abstractmethod
    def get_columns(
        self,
        connection_details: Dict[str, Any],
        db_table_name: str,
        engine: Optional[Any] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """
        Retrieve column information for a specific table.

        Args:
            connection_details: Dictionary containing connection parameters.
            db_table_name: Fully qualified table name.
            engine: Optional pre-existing engine to use.
            connection: Optional pre-existing connection to use.

        Returns:
            Column metadata for the specified table.
        """
        pass

    # ------------------------------------------------------------------
    # non-abstract methods — only RDBMS connectors need to override
    # ------------------------------------------------------------------

    def get_connection_string(self, connection_details: Dict[str, Any]) -> str:
        """
        Build a dialect-specific connection string from connection details.

        Only RDBMS connectors (SqlAlchemy, Redshift, etc.) implement this.
        Non-RDBMS connectors (S3, Google Sheets, Cassandra) raise
        ``NotImplementedError``.

        Args:
            connection_details: Dictionary containing connection parameters
                (host, port, username, password, database, driver, etc.).

        Returns:
            A connection string suitable for ``sqlalchemy.create_engine()``.

        Raises:
            NotImplementedError: If the connector does not support
                connection strings.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support get_connection_string()"
        )

    def get_engine(self, connection_details: Dict[str, Any], **pool_kwargs: Any) -> Any:
        """
        Return a SQLAlchemy ``Engine`` for the data source.

        Only RDBMS connectors implement this.

        Args:
            connection_details: Dictionary containing connection parameters.
            **pool_kwargs: Additional keyword arguments for engine pool
                configuration (e.g. ``pool_size``, ``max_overflow``).

        Returns:
            A ``sqlalchemy.engine.Engine`` instance.

        Raises:
            NotImplementedError: If the connector does not support
                SQLAlchemy engines.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support get_engine()"
        )
