"""
Core datasource utilities.

Shared helper functions and classes extracted from ``opendatapipeline`` utilities
to be used by datasource connector implementations across all apps.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from .exceptions import DataSourceException

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Standalone helpers
# ---------------------------------------------------------------------------

def map_columns(df: Any) -> List[str]:
    """
    Sanitise DataFrame column names for downstream consumption.

    Converts all column names to lowercase and replaces any non-alphanumeric
    characters with underscores.

    Args:
        df: A pandas DataFrame whose columns should be sanitised.

    Returns:
        A list of cleaned column name strings.
    """
    return [re.sub('[^0-9a-zA-Z]+', '_', col) for col in map(str.lower, df.columns)]


def get_excel_sheetnames_from_s3(s3_client: Any, bucket: str, key: str) -> List[str]:
    """
    Read Excel sheet names from a file stored in S3.

    Args:
        s3_client: A boto3 S3 client.
        bucket: The S3 bucket name.
        key: The S3 object key.

    Returns:
        A list of sheet name strings, or an empty list on failure.
    """
    try:
        import io
        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_bytes = response["Body"].read()
        import pandas as pd
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        return excel_file.sheet_names
    except Exception as e:
        logger.error("Failed to read Excel sheet names from S3 file %s: %s", key, e)
        return []


def build_tree_from_s3_keys(
    s3_keys: List[str], s3_client: Any, s3_bucket: str
) -> List[Dict[str, Any]]:
    """
    Build a hierarchical tree structure from a flat list of S3 object keys.

    Handles folder detection, file extension classification, and special
    handling for Excel files (reads sheet names).

    Args:
        s3_keys: Flat list of S3 object key strings.
        s3_client: A boto3 S3 client (used for reading Excel sheets).
        s3_bucket: The S3 bucket name.

    Returns:
        A nested list of dicts representing the key tree, where each node
        has ``title``, ``value``, ``type``, and optionally ``children``.
    """
    tree: Dict[str, Any] = {}
    for key in s3_keys:
        parts = key.strip("/").split("/")
        current_level = tree
        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1

            # If key ends with '/' and has only 1 part like 'test/', it's a folder
            if len(parts) == 1 and key.endswith("/"):
                is_last = False

            part_path = "/".join(parts[: i + 1])
            if part_path not in current_level:
                node_type = "folder"
                children: Any = {} if not is_last else None

                if is_last:
                    extension_parts = part.rsplit(".", 1)
                    ext = (
                        extension_parts[-1].lower()
                        if len(extension_parts) == 2
                        else "file"
                    )
                    node_type = ext

                    if ext in ["xlsx", "xls"]:
                        children = []
                        try:
                            logger.debug("Fetching Excel file from S3: %s", key)
                            sheet_names = get_excel_sheetnames_from_s3(
                                s3_client, s3_bucket, key
                            )
                            for sheet_name in sheet_names:
                                children.append(
                                    {
                                        "title": sheet_name,
                                        "value": f"{part_path}.{sheet_name}",
                                        "type": "sheet",
                                    }
                                )
                        except Exception as e:
                            logger.warning(
                                "Failed to load Excel sheet names for '%s': %s",
                                key,
                                str(e),
                            )

                current_level[part_path] = {
                    "title": part + ("/" if not is_last else ""),
                    "value": part_path if is_last else part_path + "/",
                    "type": node_type,
                    "children": children,
                }

            if not is_last:
                current_level = current_level[part_path]["children"]

    def convert_to_list(node_dict: Dict) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for node in node_dict.values():
            if node["type"] == "folder":
                node["children"] = convert_to_list(node["children"])
                if not node["children"]:
                    continue
            result.append(node)
        return result

    return convert_to_list(tree)


# ---------------------------------------------------------------------------
# CreateStrings — query builder helpers used by SqlAlchemy implementation
# ---------------------------------------------------------------------------

class CreateStrings:
    """
    Helper class for creating database-dialect-specific connection strings
    and SQL query strings.

    Extracted from ``opendatapipeline`` so that ``core.datasource.implementations``
    can use it without importing from ``opendatapipeline``.
    """

    def create_connection_string(
        self, connection_url_dict: Dict[str, Any], engine: str
    ) -> Any:
        """
        Generate a SQLAlchemy ``URL`` object for the given engine.

        Args:
            connection_url_dict: Dictionary with keys: ``driver``,
                ``username``, ``password``, ``host``, ``database``,
                ``port``, and optionally ``driver_name``.
            engine: The database engine identifier (e.g. ``'postgres'``,
                ``'mysql'``, ``'ms_sql_server'``).

        Returns:
            A ``sqlalchemy.engine.URL`` instance.

        Raises:
            DataSourceException: If the engine is not supported or creation
                fails.
        """
        from sqlalchemy.engine import URL

        try:
            if engine in ["ms_sql_server", "oracle", "firebird", "mysql", "postgres"]:
                if connection_url_dict.get("driver_name"):
                    connection_url = URL.create(
                        connection_url_dict["driver"],
                        username=connection_url_dict["username"],
                        password=connection_url_dict["password"],
                        host=connection_url_dict["host"],
                        database=connection_url_dict["database"],
                        port=connection_url_dict["port"],
                        query={"driver": connection_url_dict["driver_name"]},
                    )
                else:
                    connection_url = URL.create(
                        connection_url_dict["driver"],
                        username=connection_url_dict["username"],
                        password=connection_url_dict["password"],
                        host=connection_url_dict["host"],
                        database=connection_url_dict["database"],
                        port=connection_url_dict["port"],
                    )
            else:
                raise DataSourceException(f"The engine is not supported: {engine}")
            return connection_url
        except DataSourceException:
            raise
        except Exception as e:
            raise DataSourceException(
                f"Failed to generate connection url for engine '{engine}': {str(e)}"
            ) from e

    def get_query_string(self, engine: str) -> str:
        """
        Return a SQL query to test connectivity / fetch version info.

        Args:
            engine: The database engine identifier.

        Returns:
            A SQL query string.

        Raises:
            DataSourceException: If the engine is not supported.
        """
        queries = {
            "ms_sql_server": "SELECT @@VERSION;",
            "firebird": "SELECT rdb$get_context('SYSTEM', 'ENGINE_VERSION') FROM rdb$database;",
            "oracle": "SELECT * FROM v$version",
            "mysql": "SELECT VERSION()",
            "postgres": "SELECT VERSION()",
            "snowflake": "select current_version()",
            "databricks": "SELECT current_catalog()",
        }
        query = queries.get(engine)
        if query is None:
            raise DataSourceException(f"The engine is not supported: {engine}")
        return query

    def get_fetch_data_string(
        self,
        engine: str,
        catalog: str,
        columns: Optional[List[str]] = None,
        num_rows: int = 100,
    ) -> str:
        """
        Construct a SQL SELECT statement for fetching data.

        Handles dialect-specific LIMIT/TOP/FETCH syntax.

        Args:
            engine: The database engine identifier.
            catalog: Table name (may include schema prefix).
            columns: List of column names; ``None`` or ``[]`` means ``*``.
            num_rows: Maximum number of rows to return.

        Returns:
            A SQL query string.

        Raises:
            DataSourceException: If the engine is not supported.
        """
        try:
            if columns:
                col = ", ".join(columns)
            else:
                col = "*"

            if engine == "ms_sql_server":
                return f"SELECT TOP {num_rows} {col} FROM {catalog};"
            elif engine == "firebird":
                return f"SELECT FIRST {num_rows} {col} FROM {catalog};"
            elif engine == "oracle":
                if col != "*":
                    col = ", ".join(f'"{c}"' for c in columns)
                schema, table = catalog.split(".")
                catalog_value = f'"{schema.lower()}"."{table.upper()}"'
                return f"SELECT {col} FROM {catalog_value} FETCH FIRST {num_rows} ROWS ONLY"
            elif engine in ("mysql", "postgres", "snowflake", "databricks"):
                return f"SELECT {col} FROM {catalog} LIMIT {num_rows}"
            else:
                raise DataSourceException(f"The engine is not supported: {engine}")
        except DataSourceException:
            raise
        except Exception as e:
            raise DataSourceException(
                f"Failed to build fetch query for engine '{engine}': {str(e)}"
            ) from e


# ---------------------------------------------------------------------------
# DocumentDBUtils — helpers used by Couchbase / DocumentDB implementation
# ---------------------------------------------------------------------------

class DocumentDBUtils:
    """
    Utility class for Couchbase / DocumentDB operations.

    Provides document flattening, DataFrame type normalisation, and
    column conflict resolution.
    """

    def _flatten_document(
        self,
        doc: Any,
        prefix: str = "",
        max_depth: int = 3,
        current_depth: int = 0,
    ) -> Dict[str, Any]:
        """
        Recursively flatten nested JSON into a flat dict using dot notation.

        Args:
            doc: Document to flatten (dict/list/primitive).
            prefix: Key prefix for nested fields.
            max_depth: Max recursion depth.
            current_depth: Current recursion level.

        Returns:
            Flattened key-value pairs with dot-separated keys.
        """
        flattened: Dict[str, Any] = {}

        if current_depth >= max_depth:
            if prefix:
                key = prefix.rstrip(".")
                flattened[key] = (
                    json.dumps(doc) if isinstance(doc, (dict, list)) else str(doc)
                )
            return flattened

        if isinstance(doc, dict):
            for key, value in doc.items():
                new_key = f"{prefix}{key}" if prefix else key

                if isinstance(value, dict):
                    nested = self._flatten_document(
                        value, f"{new_key}.", max_depth, current_depth + 1
                    )
                    flattened.update(nested)
                elif isinstance(value, list):
                    if value and isinstance(value[0], dict):
                        flattened[new_key] = json.dumps(value)
                    else:
                        flattened[new_key] = ", ".join(str(item) for item in value)
                else:
                    flattened[new_key] = value
        else:
            key = prefix.rstrip(".") if prefix else "value"
            flattened[key] = doc

        return flattened

    def _normalize_dataframe_types(self, dataframe: Any) -> Any:
        """
        Normalise DataFrame column types for mixed-schema compatibility.

        Object columns are cast to string with null preservation;
        ``'nan'`` strings are replaced with ``pandas.NA``.

        Args:
            dataframe: Input DataFrame with potentially mixed types.

        Returns:
            DataFrame with normalised types.
        """
        import pandas as pd
        try:
            for column in dataframe.columns:
                if dataframe[column].dtype == "object":
                    non_null_values = dataframe[column].dropna()
                    if len(non_null_values) > 0:
                        dataframe[column] = dataframe[column].astype(str)
                        dataframe[column] = dataframe[column].replace("nan", pd.NA)
            return dataframe
        except Exception as e:
            logger.warning("Type normalization failed: %s", e)
            return dataframe

    def _resolve_column_conflicts(self, dataframe: Any) -> Any:
        """
        Resolve duplicate column names by appending suffix numbers.

        Args:
            dataframe: DataFrame with potentially duplicate column names.

        Returns:
            DataFrame with unique column names.
        """
        original_columns = list(dataframe.columns)
        resolved_columns: List[str] = []
        column_counts: Dict[str, int] = {}

        for col in original_columns:
            if col in column_counts:
                column_counts[col] += 1
                resolved_columns.append(f"{col}_{column_counts[col]}")
            else:
                column_counts[col] = 0
                resolved_columns.append(col)

        dataframe.columns = resolved_columns
        return dataframe
