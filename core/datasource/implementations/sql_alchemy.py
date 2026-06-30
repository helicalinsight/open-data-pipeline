"""
Core SqlAlchemy data-source connector.

Handles all SQLAlchemy-backed databases: PostgreSQL, MySQL, Snowflake,
Oracle, MS SQL Server, Firebird, and Databricks.
"""

import copy
import json
import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from sqlalchemy import MetaData, Table, create_engine, inspect, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import scoped_session, sessionmaker
import sqlalchemy.pool as pool

from core.datasource.base import DBConnection
from core.datasource.exceptions import DataSourceException
from core.datasource.utils import CreateStrings, map_columns

logger = logging.getLogger(__name__)

# Default pool constants 
DEFAULT_POOL_SIZE = 10
DEFAULT_MAX_OVERFLOW = 20
DEFAULT_POOL_TIMEOUT = 30
DEFAULT_POOL_RECYCLE = 1800

# Driver mapping — consolidates datasources.yml connection_string drivers

# TODO: instead of duplication in defining drivername, we should consider storing datasources yml at a central place. Since this is core module, we do not want to hard code and access a file stored in opendatapipeline/ module from here.
DEFAULT_DRIVERS: Dict[str, Dict[str, Any]] = {
    "postgres": {
        "drivername": "postgresql+psycopg2",
        "default_port": 5432,
    },
    "mysql": {
        "drivername": "mysql+mysqlconnector",
        "default_port": 3306,
    },
    "ms_sql_server": {
        "drivername": "mssql+pyodbc",
        "driver_name": "ODBC Driver 18 for SQL Server",
        "default_port": 1433,
    },
    "oracle": {
        "drivername": "oracle+cx_oracle",
        "default_port": 1521,
    },
    "firebird": {
        "drivername": "firebird+firebird",
        "default_port": 3050,
    },
    "snowflake": {
        "drivername": "snowflake",
        "default_port": None,
    },
    "databricks": {
        "drivername": "databricks",
        "default_port": None,
    },
}


class SqlAlchemy(DBConnection):  # pragma: no cover
    """
    SQLAlchemy-based connector supporting multiple RDBMS dialects.

    Covers: postgres, mysql, snowflake, oracle, ms_sql_server, firebird,
    and databricks.

    All ``opendatapipeline``-specific imports have been removed.  The class uses
    ``DEFAULT_DRIVERS`` for dialect resolution, standard ``logging`` for
    logs, and ``DataSourceException`` for errors.
    """

    def __init__(self) -> None:
        self.engine_dispose: Any = None

    @staticmethod
    def _normalise_connection_details(
        connection_details: Dict[str, Any], db_type: str
    ) -> Dict[str, Any]:
        """
        Normalise vendor-specific field names into canonical ones.

        E.g. Snowflake sends ``sfUser``/``sfPassword``/``sfAccountIdentifier``
        and MySQL may use ``user`` instead of ``username``.
        """
        details = dict(copy.deepcopy(connection_details))

        if db_type == "mysql":
            details.setdefault(
                "username", details.get("user")
            )

        # Snowflake alternate field names
        if details.get("sfUser"):
            details["username"] = details.get("sfUser")
            details["password"] = details.get("sfPassword")
            details["host"] = details.get("sfAccountIdentifier")
            details["database"] = details.get("sfDatabase")

        if db_type == "databricks":
            details["username"] = "token"
            details["password"] = details.get("access_token")
            details["host"] = details.get("host")
            details["http_path"] = details.get("http_path")
            details["catalog"] = details.get("catalog")
            details["schema"] = details.get("schema")
            details["database"] = details.get("schema")

        return details

    def _build_url(
        self, details: Dict[str, Any], db_type: str
    ) -> tuple:
        """
        Build a ``sqlalchemy.engine.URL`` and any ``connect_args``
        required for the given *db_type*.

        Returns:
            (url, connect_args) tuple.
        """
        driver_info = DEFAULT_DRIVERS.get(db_type)
        if driver_info is None:
            raise DataSourceException(
                f"Unsupported db_type for SqlAlchemy connector: '{db_type}'. "
                f"Supported: {sorted(DEFAULT_DRIVERS.keys())}"
            )

        connect_args: Dict[str, Any] = {}

        if db_type == "databricks":
            query_params = {}
            if details.get("http_path"):
                query_params["http_path"] = details["http_path"]
            if details.get("catalog"):
                query_params["catalog"] = details["catalog"]
            if details.get("schema"):
                query_params["schema"] = details["schema"]

            url = URL.create(
                drivername="databricks",
                username="token",
                password=details["password"],
                host=details["host"],
                database=details.get("schema"),
                query=query_params
            )

        elif db_type == "oracle":
            url = URL.create(
                drivername=driver_info["drivername"],
                username=details["username"],
                password=details["password"],
                host=details["host"],
                port=details.get("port", driver_info["default_port"]),
                database=None,  # SID not used — newer Oracle uses service_name
                query={"service_name": details["database"]},
            )

        elif db_type == "snowflake":
            # Snowflake uses account-based URL (host = account identifier)
            account = details.get("account") or details.get("host")
            url = URL.create(
                drivername="snowflake",
                username=details["username"],
                password=details["password"],
                host=account,
                database=details.get("database"),
                query={
                    k: v
                    for k, v in {
                        "warehouse": details.get("warehouse"),
                        "schema": details.get("schema"),
                        "role": details.get("role"),
                    }.items()
                    if v
                },
            )

        else:
            # Standard RDBMS: postgres, mysql, firebird, ms_sql_server
            drivername = driver_info["drivername"]
            query: Dict[str, str] = {}

            # Handle ODBC driver for MS SQL
            odbc_driver = details.get("driver_name") or driver_info.get("driver_name")
            if odbc_driver:
                query["driver"] = odbc_driver
            if db_type == "ms_sql_server":
                query["TrustServerCertificate"] = "yes"

            url = URL.create(
                drivername=drivername,
                username=details["username"],
                password=details["password"],
                host=details["host"],
                database=details.get("database"),
                port=details.get("port", driver_info.get("default_port")),
                query=query if query else {},
            )

        return url, connect_args

    def _resolve_pool_params(
        self, connection_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve pool parameters from ``connection_details["connection_pool"]``
        with sensible defaults.
        """
        default_pool = {
            "pool_size": DEFAULT_POOL_SIZE,
            "max_overflow": DEFAULT_MAX_OVERFLOW,
            "pool_timeout": DEFAULT_POOL_TIMEOUT,
            "pool_recycle": DEFAULT_POOL_RECYCLE,
        }
        pool_config = connection_details.get("connection_pool", {})
        pandas_pooling = copy.deepcopy(
            pool_config.get("pandas_pooling", default_pool)
        )
        # Strip metadata-only keys that are not pool parameters
        pandas_pooling.pop("aod_schema", None)
        pandas_pooling.pop("aod_table", None)

        resolved: Dict[str, Any] = {}
        for key, val in pandas_pooling.items():
            try:
                resolved[key] = int(val)
            except (ValueError, TypeError):
                if key == "poolclass":
                    if hasattr(pool, str(val)):
                        resolved[key] = getattr(pool, str(val))
                    else:
                        raise ValueError(f"Invalid poolclass value: {val}")
                else:
                    resolved[key] = val

        return resolved

    def connect(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
    ) -> Any:
        """
        Establish a live connection.

        Args:
            connection_details: Connection parameters dict.
            engine: Database type string (e.g. ``'postgres'``,
                ``'snowflake'``).  Also accepted as
                ``connection_details['db_type']``.

        Returns:
            A live SQLAlchemy ``Connection`` object.
        """
        db_type = engine or connection_details.get("db_type")
        if not db_type:
            raise DataSourceException("db_type must be provided.")

        try:
            logger.info("Connecting to %s ...", db_type)
            details = self._normalise_connection_details(connection_details, db_type)
            url, connect_args = self._build_url(details, db_type)
            pool_params = self._resolve_pool_params(connection_details)

            engine_obj = create_engine(url, connect_args=connect_args, **pool_params)
            self.engine_dispose = engine_obj

            cnx = engine_obj.connect()

            # Snowflake: validate the database exists
            if db_type == "snowflake":
                result = cnx.execute(text("SELECT CURRENT_DATABASE()")).fetchone()
                if not result or not result[0]:
                    raise DataSourceException(
                        f"Database {connection_details.get('database')} is not valid."
                    )

            logger.info("Connected to %s.", db_type)
            return cnx

        except DataSourceException:
            raise
        except Exception as e:
            logger.error("Error connecting to %s: %s", db_type, e, exc_info=True)
            raise DataSourceException(
                f"Failed to connect to {db_type}. Error: {e}"
            ) from e

    def test_connection(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Test the connection by executing a version query."""
        db_type = engine or connection_details.get("db_type")
        if not connection:
            connection = self.connect(connection_details, engine)

        try:
            logger.info("Testing %s connection ...", db_type)
            query = CreateStrings().get_query_string(db_type)
            result = connection.execute(text(query)).fetchone()
            if result:
                logger.info("Connection test passed.")
                return True
            return False
        except Exception as e:
            logger.error("Connection test failed for %s: %s", db_type, e, exc_info=True)
            raise DataSourceException(
                f"Failed to test the connection: {e}"
            ) from e
        finally:
            if connection:
                connection.close()
            if self.engine_dispose:
                self.engine_dispose.dispose()
            logger.info("Connection to %s closed.", db_type)

    def fetch_data(
        self,
        connection_details: Dict[str, Any],
        catalog: str,
        columns: Optional[List[str]] = None,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
        num_rows: int = 100,
    ) -> Any:
        """Fetch rows from a table, returning a pandas DataFrame."""
        import pandas as pd

        db_type = engine or connection_details.get("db_type")
        if not catalog:
            raise DataSourceException("Catalog (table name) must be provided.")
        if columns is None:
            columns = []
        if not connection:
            connection = self.connect(connection_details, engine)

        try:
            if db_type == "snowflake":
                warehouse = connection_details.get("warehouse")
                if not warehouse:
                    raise DataSourceException(
                        "Please edit the DataSource and add Warehouse details."
                    )
                connection.execute(text(f"USE WAREHOUSE {warehouse}"))

            logger.info("Fetching data from %s ...", db_type)
            select_query = CreateStrings().get_fetch_data_string(
                db_type, catalog, columns, num_rows=num_rows
            )
            dataframe = pd.read_sql(select_query, connection)
            dataframe.columns = map_columns(dataframe)
            logger.info("Fetched data successfully.")
            return dataframe

        except DataSourceException:
            raise
        except Exception as e:
            cleaned = re.sub(r"\[SQL:.*\]", "", str(e)).strip()
            logger.error("Failed to fetch data from %s: %s", db_type, e, exc_info=True)
            raise DataSourceException(
                f"Failed to fetch the data: {cleaned}"
            ) from e
        finally:
            if connection:
                connection.close()
            if self.engine_dispose:
                self.engine_dispose.dispose()
            logger.info("Connection to %s closed.", db_type)

    def get_metadata(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Retrieve schemas and tables from the database."""
        db_type = engine or connection_details.get("db_type")
        if not connection:
            connection = self.connect(connection_details, engine)

        try:
            logger.info("Getting metadata for %s ...", db_type)

            if db_type == "snowflake":
                warehouse = connection_details.get("warehouse")
                if not warehouse:
                    raise DataSourceException(
                        "Please edit the DataSource and add Warehouse details."
                    )
                connection.execute(text(f"USE WAREHOUSE {warehouse}"))

            catalog_name = connection_details.get("catalog")
            if db_type == "databricks" and not catalog_name:
                raise DataSourceException(
                    "Missing 'catalog' for Databricks. Please add it in the connection details."
                )

            metadata = MetaData()
            inspector = inspect(connection)

            # Read optional schema / table filters from pool config
            pool_config = connection_details.get("connection_pool", {})
            pandas_pooling = pool_config.get("pandas_pooling", {})

            selected_schemas = pandas_pooling.get("aod_schema")
            if selected_schemas is not None:
                try:
                    selected_schemas = json.loads(selected_schemas)
                    selected_schemas = [s.lower() for s in selected_schemas]
                except Exception as exc:
                    raise ValueError(
                        f"Invalid format for schemas, a list of strings expected - {exc}"
                    ) from exc

            selected_tables = pandas_pooling.get("aod_table")
            if selected_tables is not None:
                try:
                    selected_tables = json.loads(selected_tables)
                    selected_tables = [t.lower() for t in selected_tables]
                except Exception as exc:
                    raise ValueError(
                        f"Invalid format for tables, a list of strings expected - {exc}"
                    ) from exc

            # Retrieve schemas
            try:
                if db_type == "databricks":
                    schemas = inspector.get_schema_names(catalog=catalog_name)
                else:
                    schemas = inspector.get_schema_names()
            except Exception as exc:
                logger.warning("Unable to get schemas: %s", exc, exc_info=True)
                schemas = []

            if selected_schemas is not None and schemas:
                filtered = [s for s in selected_schemas if s in schemas]
                if not filtered:
                    raise ValueError(
                        f"{selected_schemas} are not present in the schemas list from db {schemas}"
                    )
                schemas = filtered

            if connection_details.get("database") in schemas:
                schemas = [connection_details["database"]]

            data_catalog: List[Dict[str, Any]] = []

            if schemas:
                for schema_name in schemas:
                    schema_info: Dict[str, Any] = {
                        "title": schema_name,
                        "value": schema_name,
                        "children": [],
                    }
                    quoted = (
                        f'"{schema_name}"'
                        if schema_name[0].isdigit()
                        else schema_name
                    )

                    # Get table names
                    try:
                        if db_type == "databricks":
                            result = connection.execute(
                                text(f"SHOW TABLES IN {catalog_name}.{schema_name}")
                            ).fetchall()
                            table_names = [row.tableName for row in result]
                        else:
                            table_names = inspector.get_table_names(schema=quoted)
                    except Exception as exc:
                        table_names = []
                        raise DataSourceException(
                            "Failed to get table names"
                        ) from exc

                    if selected_tables is not None:
                        table_names = [
                            t for t in table_names if t.lower() in selected_tables
                        ]

                    if db_type in ("snowflake", "databricks"):
                        for table_name in table_names:
                            schema_info["children"].append(
                                {
                                    "title": table_name,
                                    "value": f"{schema_name}.{table_name}",
                                }
                            )
                    else:
                        metadata.reflect(
                            bind=connection, schema=quoted, only=table_names
                        )
                        for tbl_name, _tbl in metadata.tables.items():
                            if schema_name != tbl_name.split(".")[0].strip('"'):
                                continue
                            schema_info["children"].append(
                                {
                                    "title": tbl_name.split(".")[-1],
                                    "value": tbl_name,
                                }
                            )

                    data_catalog.append(schema_info)
            else:
                try:
                    table_names = inspector.get_table_names()
                except Exception as exc:
                    table_names = []
                    raise DataSourceException(
                        "Failed to get table names"
                    ) from exc

                if selected_tables is not None:
                    table_names = [
                        t for t in table_names if t.lower() in selected_tables
                    ]

                db_entry: Dict[str, Any] = {
                    "title": connection_details["database"],
                    "value": connection_details["database"],
                    "children": [],
                }
                for table_name in table_names:
                    db_entry["children"].append(
                        {
                            "title": table_name.split(".")[-1],
                            "value": table_name,
                        }
                    )
                data_catalog.append(db_entry)

            return data_catalog

        except ValueError as ve:
            logger.error("Input validation error: %s", ve, exc_info=True)
            raise DataSourceException(f"Invalid input: {ve}") from ve
        except DataSourceException:
            raise
        except Exception as e:
            cleaned = re.sub(r"\[SQL:.*\]", "", str(e)).strip()
            logger.error("Failed to get metadata from %s: %s", db_type, e, exc_info=True)
            raise DataSourceException(
                f"Failed to get metadata: {cleaned}"
            ) from e
        finally:
            if connection:
                connection.close()
            if self.engine_dispose:
                self.engine_dispose.dispose()
            logger.info("Connection to %s closed.", db_type)

    def get_columns(
        self,
        connection_details: Dict[str, Any],
        db_table_name: str,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Retrieve column names for a given table."""
        db_type = engine or connection_details.get("db_type")
        if not connection:
            connection = self.connect(connection_details, engine)

        try:
            if db_type == "snowflake":
                warehouse = connection_details.get("warehouse")
                if not warehouse:
                    raise DataSourceException(
                        "Please edit the DataSource and add Warehouse details."
                    )
                connection.execute(text(f"USE WAREHOUSE {warehouse}"))

            if "." in db_table_name:
                schema, table_name = db_table_name.split(".")
                schema = f'"{schema}"' if schema[0].isdigit() else schema
            else:
                schema = None
                table_name = db_table_name

            metadata = MetaData()
            if schema:
                tbl = Table(table_name, metadata, autoload_with=connection, schema=schema)
            else:
                tbl = Table(table_name, metadata, autoload_with=connection)

            return [col.name for col in tbl.columns]

        except DataSourceException:
            raise
        except Exception as e:
            cleaned = re.sub(r"\[SQL:.*\]", "", str(e)).strip()
            logger.error("Failed to get columns from %s: %s", db_type, e, exc_info=True)
            raise DataSourceException(
                f"Failed to get columns for table {db_table_name}: {cleaned}"
            ) from e
        finally:
            if connection:
                connection.close()
            if self.engine_dispose:
                self.engine_dispose.dispose()
            logger.info("Connection to %s closed.", db_type)

    def get_connection_string(
        self, connection_details: Dict[str, Any]
    ) -> str:
        """
        Build a dialect-specific SQLAlchemy connection string.

        Merges logic from ``opendatapipeline`` datasources.yml driver mappings
        and ``dlt_server_app`` ``ConnectionStringBuilder``.

        Args:
            connection_details: Must include ``db_type`` and the
                appropriate host/port/username/password/database fields.

        Returns:
            A string URL suitable for ``sqlalchemy.create_engine()``.
        """
        db_type = connection_details.get("db_type")
        if not db_type:
            raise DataSourceException(
                "connection_details must include 'db_type'."
            )

        details = self._normalise_connection_details(connection_details, db_type)
        url, _connect_args = self._build_url(details, db_type)
        return url.render_as_string(hide_password=False)

    def get_engine(
        self, connection_details: Dict[str, Any], **pool_kwargs: Any
    ) -> Any:
        """
        Create and return a SQLAlchemy ``Engine``.

        Args:
            connection_details: Must include ``db_type`` and the
                appropriate connection fields.
            **pool_kwargs: Override pool settings.  Accepted keys:
                ``pool_size``, ``max_overflow``, ``pool_timeout``,
                ``pool_recycle``, ``pool_pre_ping``.

        Returns:
            A ``sqlalchemy.engine.Engine`` instance.
        """
        db_type = connection_details.get("db_type")
        if not db_type:
            raise DataSourceException(
                "connection_details must include 'db_type'."
            )

        details = self._normalise_connection_details(connection_details, db_type)
        url, connect_args = self._build_url(details, db_type)

        # Merge default pool params with caller overrides
        engine_kwargs: Dict[str, Any] = {
            "pool_size": DEFAULT_POOL_SIZE,
            "max_overflow": DEFAULT_MAX_OVERFLOW,
            "pool_timeout": DEFAULT_POOL_TIMEOUT,
            "pool_recycle": DEFAULT_POOL_RECYCLE,
            "pool_pre_ping": True,
        }
        engine_kwargs.update(pool_kwargs)

        if connect_args:
            engine_kwargs["connect_args"] = connect_args

        # DB-type-specific tweaks
        if db_type == "ms_sql_server":
            engine_kwargs.setdefault("fast_executemany", True)

        logger.info(
            "Creating engine for %s (pool_size=%s, max_overflow=%s)",
            db_type,
            engine_kwargs.get("pool_size"),
            engine_kwargs.get("max_overflow"),
        )
        return create_engine(url, **engine_kwargs)
