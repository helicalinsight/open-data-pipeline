"""
Core S3 data-source connector.

Handles connections to Amazon S3 buckets and loading of various file
formats (CSV, Excel, Parquet, JSON) into pandas DataFrames.
"""

import io
import logging
from typing import Any, Dict, List, Optional

from core.datasource.base import DBConnection
from core.datasource.exceptions import DataSourceException
from core.datasource.utils import build_tree_from_s3_keys, map_columns

logger = logging.getLogger(__name__)


class S3(DBConnection):
    """
    Amazon S3 connector using ``boto3``.

    ``get_connection_string()`` and ``get_engine()`` raise
    ``NotImplementedError`` — S3 is not an RDBMS.
    """

    def connect(self, connection_details: Dict[str, Any], engine: Optional[str] = None) -> Any:
        """Create and return a boto3 S3 client."""
        import boto3

        try:
            access_key = connection_details.get("aws_access_key")
            secret_key = connection_details.get("aws_secret_key")
            region = connection_details.get("aws_region")

            if not all([access_key, secret_key, region]):
                raise ValueError(
                    "Missing one or more required AWS credentials: "
                    "'aws_access_key', 'aws_secret_key', or 'aws_region'"
                )

            client = boto3.client(
                "s3",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
            )
            logger.info("Connected to S3.")
            return client
        except Exception as e:
            logger.error("Error connecting to S3: %s", e, exc_info=True)
            raise DataSourceException(f"Error while connecting to S3. {e}") from e

    def test_connection(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Test access to the S3 bucket by listing objects."""
        if not connection:
            connection = self.connect(connection_details)
        try:
            bucket = connection_details.get("bucket_name")
            connection.list_objects_v2(Bucket=bucket, MaxKeys=1)
            logger.info("S3 connection test passed.")
            return True
        except Exception as e:
            logger.error("Failed to test S3 connection: %s", e, exc_info=True)
            raise DataSourceException(f"Error testing S3 connection: {e}") from e

    def fetch_data(
        self,
        connection_details: Dict[str, Any],
        catalog: str,
        columns: Optional[List[str]] = None,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
        num_rows: int = 100,
    ) -> Any:
        """Fetch data from an S3 file as a DataFrame."""
        import pandas as pd

        if not connection:
            connection = self.connect(connection_details)
        if columns is None:
            columns = []

        bucket = connection_details.get("bucket_name")
        file_key = catalog
        sheet_name = None

        # Handle xlsx/xls files with sheet names: file_name.ext.sheet_name
        if catalog.count(".") == 2:
            for ext in ("xlsx", "xls"):
                dot_ext = f".{ext}."
                if dot_ext in catalog:
                    parts = catalog.split(dot_ext, 1)
                    if len(parts) == 2:
                        file_key = f"{parts[0]}.{ext}"
                        sheet_name = parts[1].strip()
                    break

        logger.info("Fetching from S3: key=%s, sheet=%s", file_key, sheet_name)

        try:
            file_obj = connection.get_object(Bucket=bucket, Key=file_key)
            file_extension = file_key.lower().split(".")[-1]
            content = file_obj["Body"].read()

            if file_extension == "csv":
                df = pd.read_csv(io.BytesIO(content))
            elif file_extension in ("parquet", "pq"):
                df = pd.read_parquet(io.BytesIO(content))
            elif file_extension in ("xls", "xlsx"):
                df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
            elif file_extension == "json":
                df = pd.read_json(io.BytesIO(content))
            else:
                raise DataSourceException(f"Unsupported file type: {file_extension}")

            df.columns = map_columns(df)
            if columns:
                df = df[columns]
            df = df.head(num_rows)
            logger.info("Fetched data from S3.")
            return df
        except DataSourceException:
            raise
        except Exception as e:
            logger.error("Failed to fetch data from S3: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to fetch S3 data: {e}") from e

    def get_metadata(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Return a hierarchical tree of files in the S3 bucket."""
        if not connection:
            connection = self.connect(connection_details)
        bucket = connection_details.get("bucket_name")
        try:
            objects = connection.list_objects_v2(Bucket=bucket)
            all_keys = [obj["Key"] for obj in objects.get("Contents", [])]
            nested_files = build_tree_from_s3_keys(all_keys, connection, bucket)
            logger.info("Fetched S3 metadata.")
            return nested_files
        except Exception as e:
            logger.error("Failed to fetch S3 metadata: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to get metadata: {e}") from e

    def get_columns(
        self,
        connection_details: Dict[str, Any],
        db_table_name: str,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Read the file and return column names."""
        df = self.fetch_data(
            connection_details, db_table_name, num_rows=1, connection=connection
        )
        return list(df.columns)
