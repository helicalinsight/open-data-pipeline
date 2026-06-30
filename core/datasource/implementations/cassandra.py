"""
Core Cassandra data-source connector.

Handles connections to Apache Cassandra databases using the
cassandra-driver Python client.
"""

import logging
from typing import Any, Dict, List, Optional

from core.datasource.base import DBConnection
from core.datasource.exceptions import DataSourceException
from core.datasource.utils import map_columns

logger = logging.getLogger(__name__)


class Cassandra(DBConnection):
    """
    Cassandra connector using the DataStax Python driver.

    ``connect()`` returns a ``(session, cluster)`` tuple.
    ``get_connection_string()`` and ``get_engine()`` raise
    ``NotImplementedError`` — Cassandra is not an RDBMS.
    """

    def connect(self, connection_details: Dict[str, Any], engine: Optional[str] = None) -> Any:
        """Establish a Cassandra connection. Returns ``(session, cluster)``."""
        from cassandra.cluster import Cluster
        from cassandra.auth import PlainTextAuthProvider

        try:
            username = connection_details.get("username")
            password = connection_details.get("password")
            host = connection_details.get("host")
            port = connection_details.get("port")

            pool_params = connection_details.get("connection_pool", {})
            pandas_pooling = pool_params.get("pandas_pooling", {})

            pool_kwargs: Dict[str, Any] = {}
            for key, val in pandas_pooling.items():
                try:
                    pool_kwargs[key] = int(val)
                except (ValueError, TypeError):
                    pool_kwargs[key] = val

            auth_provider = PlainTextAuthProvider(username=username, password=password)
            cluster = Cluster([host], port=port, auth_provider=auth_provider, **pool_kwargs)
            session = cluster.connect()
            logger.info("Connected to Cassandra.")
            return session, cluster
        except Exception as e:
            logger.error("Error connecting to Cassandra: %s", e, exc_info=True)
            raise DataSourceException(f"Error while connecting to Cassandra. {e}") from e

    def test_connection(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Test the Cassandra connection."""
        if not connection:
            session, cluster = self.connect(connection_details)
        else:
            session, cluster = connection
        try:
            result = session.execute("SELECT release_version FROM system.local")
            if result:
                logger.info("Cassandra connection test passed.")
                return True
            return False
        except Exception as e:
            logger.error("Cassandra test failed: %s", e, exc_info=True)
            raise DataSourceException(f"Error while testing Cassandra connection: {e}") from e
        finally:
            if cluster:
                cluster.shutdown()
            logger.info("Closed Cassandra connection.")

    def fetch_data(
        self,
        connection_details: Dict[str, Any],
        catalog: str,
        columns: Optional[List[str]] = None,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
        num_rows: int = 100,
    ) -> Any:
        """Fetch rows from a Cassandra table as a DataFrame."""
        import pandas as pd

        if not connection:
            session, cluster = self.connect(connection_details)
        else:
            session, cluster = connection
        try:
            col = ", ".join(columns) if columns else "*"
            select_query = f"SELECT {col} FROM {catalog} LIMIT {num_rows}"
            result_set = session.execute(select_query)
            dataframe = pd.DataFrame(result_set)
            dataframe = dataframe.astype(
                {c: "str" for c in dataframe.select_dtypes(include=["object"]).columns}
            )
            dataframe.columns = map_columns(dataframe)
            logger.info("Fetched data from Cassandra.")
            return dataframe
        except Exception as e:
            logger.error("Failed to fetch data from Cassandra: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to fetch the data: {e}") from e
        finally:
            if cluster:
                cluster.shutdown()
            logger.info("Closed Cassandra connection.")

    def get_metadata(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Retrieve keyspaces and tables from Cassandra."""
        if not connection:
            session, cluster = self.connect(connection_details)
        else:
            session, cluster = connection
        try:
            metadata = cluster.metadata
            cluster_metadata: List[Dict[str, Any]] = []
            for keyspace_name in metadata.keyspaces:
                tables = metadata.keyspaces[keyspace_name].tables.keys()
                cluster_metadata.append({
                    "title": keyspace_name,
                    "value": keyspace_name,
                    "children": [
                        {"title": t, "value": f"{keyspace_name}.{t}"}
                        for t in tables
                    ],
                })
            logger.info("Fetched Cassandra metadata.")
            return cluster_metadata
        except Exception as e:
            logger.error("Failed to get Cassandra metadata: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to get the metadata: {e}") from e
        finally:
            if cluster:
                cluster.shutdown()
            logger.info("Closed Cassandra connection.")

    def get_columns(
        self,
        connection_details: Dict[str, Any],
        db_table_name: str,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Retrieve column names for a Cassandra table."""
        if not connection:
            session, cluster = self.connect(connection_details)
        else:
            session, cluster = connection
        try:
            keyspace_name, table_name = db_table_name.split(".")
            table_metadata = cluster.metadata.keyspaces[keyspace_name].tables[table_name]
            columns = list(table_metadata.columns.keys())
            logger.info("Fetched columns for %s.%s.", keyspace_name, table_name)
            return columns
        except Exception as e:
            logger.error("Error fetching columns from Cassandra: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to fetch the columns: {e}") from e
        finally:
            if cluster:
                cluster.shutdown()
            logger.info("Closed Cassandra connection.")
