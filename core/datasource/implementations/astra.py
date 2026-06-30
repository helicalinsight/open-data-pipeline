"""
Core Astra (DataStax Astra DB) data-source connector.

Handles connections to Astra DB using the secure-connect bundle
and the DataStax Cassandra Python driver.
"""

import logging
from typing import Any, Dict, List, Optional

from core.datasource.base import DBConnection
from core.datasource.exceptions import DataSourceException
from core.datasource.utils import map_columns

logger = logging.getLogger(__name__)


class Astra(DBConnection):
    """
    Astra DB connector using the DataStax Python driver with secure
    connect bundle.

    ``connect()`` returns a ``(session, cluster)`` tuple.
    ``get_connection_string()`` and ``get_engine()`` raise
    ``NotImplementedError`` — Astra is not an RDBMS.
    """

    def connect(self, connection_details: Dict[str, Any], engine: Optional[str] = None) -> Any:
        """Establish an Astra connection. Returns ``(session, cluster)``."""
        from cassandra.cluster import Cluster
        from cassandra.auth import PlainTextAuthProvider

        try:
            bundle = connection_details.get("bundle")
            client_id = connection_details.get("client_id")
            secret = connection_details.get("secret")

            auth_provider = PlainTextAuthProvider(username=client_id, password=secret)

            pool_params = connection_details.get("connection_pool", {})
            pandas_pooling = pool_params.get("pandas_pooling", {})

            pool_kwargs: Dict[str, Any] = {}
            for key, val in pandas_pooling.items():
                try:
                    pool_kwargs[key] = int(val)
                except (ValueError, TypeError):
                    pool_kwargs[key] = val

            cluster = Cluster(
                cloud={"secure_connect_bundle": bundle.get("file")},
                auth_provider=auth_provider,
                **pool_kwargs,
            )
            session = cluster.connect()
            logger.info("Connected to Astra.")
            return session, cluster
        except Exception as e:
            logger.error("Error connecting to Astra: %s", e, exc_info=True)
            raise DataSourceException(f"Error while connecting to Astra. {e}") from e

    def test_connection(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Test the Astra connection."""
        if not connection:
            session, cluster = self.connect(connection_details)
        else:
            session, cluster = connection
        try:
            result = session.execute("SELECT release_version FROM system.local")
            if result:
                logger.info("Astra connection test passed.")
                return True
            return False
        except Exception as e:
            logger.error("Astra test failed: %s", e, exc_info=True)
            raise DataSourceException(f"Error while testing Astra connection: {e}") from e
        finally:
            if cluster:
                cluster.shutdown()
            logger.info("Closed Astra connection.")

    def fetch_data(
        self,
        connection_details: Dict[str, Any],
        catalog: str,
        columns: Optional[List[str]] = None,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
        num_rows: int = 100,
    ) -> Any:
        """Fetch rows from an Astra table as a DataFrame."""
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
            logger.info("Fetched data from Astra.")
            return dataframe
        except Exception as e:
            logger.error("Failed to fetch data from Astra: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to fetch the data: {e}") from e
        finally:
            if cluster:
                cluster.shutdown()
            logger.info("Closed Astra connection.")

    def get_metadata(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Retrieve keyspaces and tables from Astra."""
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
            logger.info("Fetched Astra metadata.")
            return cluster_metadata
        except Exception as e:
            logger.error("Failed to get Astra metadata: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to get the metadata: {e}") from e
        finally:
            if cluster:
                cluster.shutdown()
            logger.info("Closed Astra connection.")

    def get_columns(
        self,
        connection_details: Dict[str, Any],
        db_table_name: str,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Retrieve column names for an Astra table."""
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
            logger.error("Error fetching columns from Astra: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to fetch the columns: {e}") from e
        finally:
            if cluster:
                cluster.shutdown()
            logger.info("Closed Astra connection.")
