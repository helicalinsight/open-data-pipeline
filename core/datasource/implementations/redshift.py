"""
Core Redshift data-source connector.

Handles connections to Amazon Redshift using psycopg2.
Also provides ``get_connection_string()`` and ``get_engine()`` for
SQLAlchemy-based access (e.g. from dlt_server_app).
"""

import logging
from typing import Any, Dict, List, Optional

from core.datasource.base import DBConnection
from core.datasource.exceptions import DataSourceException

logger = logging.getLogger(__name__)

DEFAULT_REDSHIFT_PORT = 5439


class Redshift(DBConnection):
    """
    Amazon Redshift connector using psycopg2 for native access.

    Also implements ``get_connection_string()`` and ``get_engine()``
    to produce a ``redshift+psycopg2://`` SQLAlchemy URL.
    """

    def connect(self, connection_details: Dict[str, Any], engine: Optional[str] = None) -> Any:
        """Establish a psycopg2 connection to Redshift."""
        import psycopg2

        try:
            connection = psycopg2.connect(
                dbname=connection_details.get("database"),
                user=connection_details.get("username"),
                password=connection_details.get("password"),
                host=connection_details.get("host"),
                port=connection_details.get("port", DEFAULT_REDSHIFT_PORT),
            )
            logger.info("Connected to Redshift.")
            return connection
        except Exception as e:
            logger.error("Error connecting to Redshift: %s", e, exc_info=True)
            raise DataSourceException(f"Error while connecting to Redshift. {e}") from e

    def test_connection(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Test the Redshift connection."""
        if not connection:
            connection = self.connect(connection_details)
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            if version:
                logger.info("Redshift connection test passed.")
                return True
            return False
        except Exception as e:
            logger.error("Redshift test failed: %s", e, exc_info=True)
            raise DataSourceException(f"Error while testing Redshift: {e}") from e
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            logger.info("Closed Redshift connection.")

    def fetch_data(
        self,
        connection_details: Dict[str, Any],
        catalog: str,
        columns: Optional[List[str]] = None,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
        num_rows: int = 100,
    ) -> Any:
        """Fetch rows from Redshift as a DataFrame."""
        import pandas as pd

        if not connection:
            connection = self.connect(connection_details)
        cursor = connection.cursor()
        try:
            col = ", ".join(columns) if columns else "*"
            select_query = f"SELECT {col} FROM {catalog} LIMIT {num_rows};"
            cursor.execute(select_query)
            data = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]
            dataframe = pd.DataFrame(data, columns=colnames)
            logger.info("Fetched data from Redshift.")
            return dataframe
        except Exception as e:
            logger.error("Failed to fetch data from Redshift: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to fetch the data: {e}") from e
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            logger.info("Closed Redshift connection.")

    def get_metadata(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Retrieve schemas and tables from Redshift."""
        if not connection:
            connection = self.connect(connection_details)
        cursor = connection.cursor()
        try:
            database_name = connection_details.get("database")
            data_catalog: List[Dict[str, Any]] = []

            if database_name:
                databases = [(database_name,)]
            else:
                cursor.execute(
                    "SELECT datname FROM pg_database WHERE datistemplate = false;"
                )
                databases = cursor.fetchall()

            for db_row in databases:
                db_name = db_row[0]
                database_entry = {"title": db_name, "value": db_name, "children": []}

                cursor.execute(
                    "SELECT DISTINCT schemaname FROM pg_tables "
                    "WHERE schemaname NOT LIKE 'pg_%' AND schemaname != 'information_schema';"
                )
                schemas = cursor.fetchall()

                for schema_row in schemas:
                    schema_name = schema_row[0]
                    schema_entry = {"title": schema_name, "value": schema_name, "children": []}

                    cursor.execute(
                        f"SELECT table_name FROM {db_name}.information_schema.tables "
                        f"WHERE table_schema = '{schema_name}' ORDER BY table_name;"
                    )
                    tables = cursor.fetchall()

                    for table_row in tables:
                        table_name = table_row[0]
                        if database_name:
                            table_entry = {"title": table_name, "value": f"{schema_name}.{table_name}"}
                        else:
                            table_entry = {"title": table_name, "value": f"{db_name}_{schema_name}.{table_name}"}
                        schema_entry["children"].append(table_entry)

                    database_entry["children"].append(schema_entry)
                data_catalog.append(database_entry)

            logger.info("Fetched Redshift metadata.")
            return data_catalog
        except Exception as e:
            logger.error("Failed to get Redshift metadata: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to get metadata: {e}") from e
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            logger.info("Closed Redshift connection.")

    def get_columns(
        self,
        connection_details: Dict[str, Any],
        db_table_name: str,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Retrieve column names for a Redshift table."""
        if not connection:
            connection = self.connect(connection_details)
        cursor = connection.cursor()
        schema, table = db_table_name.split(".")
        try:
            query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
            """
            cursor.execute(query, (schema, table))
            columns = [row[0] for row in cursor.fetchall()]
            logger.info("Fetched columns for %s.%s.", schema, table)
            return columns
        except Exception as e:
            logger.error("Failed to fetch columns for %s.%s: %s", schema, table, e, exc_info=True)
            raise DataSourceException(
                f"Failed to get columns for {schema}.{table}: {e}"
            ) from e
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            logger.info("Closed Redshift connection.")

    # ------------------------------------------------------------------
    # RDBMS helpers for dlt_server_app / migration use-cases
    # ------------------------------------------------------------------

    def get_connection_string(self, connection_details: Dict[str, Any]) -> str:
        """
        Build a SQLAlchemy connection string for Redshift.

        Returns a ``redshift+psycopg2://`` URL.
        """
        from sqlalchemy.engine import URL

        try:
            url = URL.create(
                drivername="redshift+psycopg2",
                username=connection_details.get("username"),
                password=connection_details.get("password"),
                host=connection_details.get("host"),
                port=connection_details.get("port", DEFAULT_REDSHIFT_PORT),
                database=connection_details.get("database"),
            )
            return url.render_as_string(hide_password=False)
        except Exception as e:
            raise DataSourceException(
                f"Failed to build Redshift connection string: {e}"
            ) from e

    def get_engine(self, connection_details: Dict[str, Any], **pool_kwargs: Any) -> Any:
        """
        Create a SQLAlchemy engine for Redshift.
        """
        from sqlalchemy import create_engine

        conn_str = self.get_connection_string(connection_details)
        defaults = {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 30,
            "pool_recycle": 1800,
            "pool_pre_ping": True,
        }
        defaults.update(pool_kwargs)
        logger.info("Creating Redshift engine.")
        return create_engine(conn_str, **defaults)
