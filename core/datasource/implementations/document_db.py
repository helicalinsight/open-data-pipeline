"""
Core Unified Document DB data-source connector.

Supports Couchbase with extensibility for future document databases
(MongoDB, DynamoDB, CouchDB).
"""

import logging
from typing import Any, Dict, List, Optional

from core.datasource.base import DBConnection
from core.datasource.exceptions import DataSourceException
from core.datasource.utils import DocumentDBUtils

logger = logging.getLogger(__name__)


class UnifiedDocumentDB(DBConnection):
    """
    Unified Document Database connector.

    Currently supports Couchbase. Uses engine-based routing to dispatch
    operations to database-specific handlers.

    ``get_connection_string()`` and ``get_engine()`` raise
    ``NotImplementedError`` — document databases are not RDBMS.
    """

    def __init__(self) -> None:
        super().__init__()
        self._connection: Any = None
        self._operations: Any = None
        self.document_utils = DocumentDBUtils()

        self._connection_handlers = {
            "couchbase": self._get_couchbase_operations,
        }

    def __del__(self) -> None:
        """Automatic cleanup when object is destroyed."""
        if self._connection is not None and self._operations is not None:
            try:
                self._operations.cleanup_connection(self._connection)
            except Exception as e:
                logger.warning("Cleanup warning: %s", e)
            finally:
                self._connection = None
                self._operations = None

    # ------------------------------------------------------------------
    # DBConnection abstract methods
    # ------------------------------------------------------------------

    def connect(self, connection_details: Dict[str, Any], engine: Optional[str] = None) -> Any:
        """Connect to the document database identified by *engine*."""
        try:
            if self._connection is None:
                if engine not in self._connection_handlers:
                    raise DataSourceException(
                        f"Unsupported document DB engine: '{engine}'. "
                        f"Supported: {sorted(self._connection_handlers.keys())}"
                    )
                self._operations = self._connection_handlers[engine]()
                self._connection = self._operations.connect(connection_details)
                logger.info("Connected to %s.", engine)
            return self._connection
        except DataSourceException:
            raise
        except Exception as e:
            logger.error("Connection failed for %s: %s", engine, e, exc_info=True)
            raise DataSourceException(f"Connection failed for {engine}: {e}") from e

    def test_connection(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Test the document database connection."""
        try:
            if self._connection is None:
                self._operations = self._connection_handlers[engine]()
                self._connection = self._operations.connect(connection_details)

            result = self._operations.test_connection(self._connection)
            logger.info("Connection test for %s: %s", engine, "passed" if result else "failed")
            return result
        except Exception as e:
            logger.error("Connection test failed for %s: %s", engine, e, exc_info=True)
            raise DataSourceException(f"Connection test failed for {engine}: {e}") from e

    def fetch_data(
        self,
        connection_details: Dict[str, Any],
        catalog: str,
        columns: Optional[List[str]] = None,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
        num_rows: int = 100,
    ) -> Any:
        """Fetch documents from the collection as a DataFrame."""
        import pandas as pd

        try:
            if self._connection is None:
                self._operations = self._connection_handlers[engine]()
                self._connection = self._operations.connect(connection_details)

            catalog_info = self._operations.parse_catalog(catalog, connection_details)
            query_info = self._operations.build_query(catalog_info, columns or [], num_rows)
            raw_documents = self._operations.execute_query(self._connection, query_info)

            if not raw_documents:
                return pd.DataFrame()

            processed_data = self._process_documents(raw_documents, engine)

            if processed_data["rows"]:
                dataframe = pd.DataFrame(processed_data["rows"])
                dataframe = self.document_utils._normalize_dataframe_types(dataframe)
                logger.info(
                    "Fetched %d rows from %s:%s.", len(dataframe), engine, catalog
                )
                return dataframe

            return pd.DataFrame()

        except Exception as e:
            logger.error("Data fetch failed for %s: %s", engine, e, exc_info=True)
            raise DataSourceException(f"Failed to fetch data from {engine}: {e}") from e

    def get_metadata(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Retrieve hierarchical metadata (scopes / collections)."""
        try:
            if self._connection is None:
                self._operations = self._connection_handlers[engine]()
                self._connection = self._operations.connect(connection_details)

            metadata = self._operations.get_metadata(self._connection, connection_details)
            logger.info("Fetched metadata from %s.", engine)
            return metadata
        except Exception as e:
            logger.error("Metadata retrieval failed for %s: %s", engine, e, exc_info=True)
            raise DataSourceException(f"Failed to get metadata from {engine}: {e}") from e

    def get_columns(
        self,
        connection_details: Dict[str, Any],
        db_table_name: str,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
        sample_size: int = 100,
    ) -> Any:
        """Discover top-level field names by sampling documents."""
        try:
            if self._connection is None:
                self._operations = self._connection_handlers[engine]()
                self._connection = self._operations.connect(connection_details)

            catalog_info = self._operations.parse_catalog(db_table_name, connection_details)
            sample_query = self._operations.build_query(catalog_info, [], sample_size)
            sample_documents = self._operations.execute_query(self._connection, sample_query)

            if not sample_documents:
                return []

            all_columns: set = set()
            for doc in sample_documents:
                try:
                    clean_doc = self._clean_document(doc, engine)
                    if isinstance(clean_doc, dict):
                        all_columns.update(clean_doc.keys())
                except Exception:
                    continue

            columns = sorted(list(all_columns))
            logger.info("Discovered %d columns in %s:%s.", len(columns), engine, db_table_name)
            return columns
        except Exception as e:
            logger.error("Column discovery failed for %s: %s", engine, e, exc_info=True)
            raise DataSourceException(f"Failed to discover columns from {engine}: {e}") from e

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _process_documents(self, documents: List[Dict], engine: str) -> Dict:
        """Process documents preserving original structure."""
        processed_rows: List[Dict] = []
        processing_errors = 0

        for doc in documents:
            try:
                clean_doc = self._clean_document(doc, engine)
                processed_rows.append(clean_doc)
            except Exception:
                processing_errors += 1
                continue

        return {
            "rows": processed_rows,
            "total_documents": len(documents),
            "processed_documents": len(processed_rows),
            "processing_errors": processing_errors,
        }

    @staticmethod
    def _clean_document(doc: Dict, engine: str) -> Dict:
        """Apply engine-specific document cleaning."""
        if engine == "couchbase":
            if isinstance(doc, dict) and len(doc) == 1:
                inner_doc = list(doc.values())[0]
                if isinstance(inner_doc, dict):
                    return inner_doc
            return doc
        return doc

    def _get_couchbase_operations(self) -> "CouchbaseOperations":
        """Factory method for Couchbase operations handler."""
        return CouchbaseOperations()


# ======================================================================
# Couchbase-specific operations
# ======================================================================

class CouchbaseOperations:
    """Couchbase-specific connection, query, and metadata operations."""

    def connect(self, connection_details: Dict[str, Any]) -> Any:
        """Create Couchbase connection. Returns ``(cluster, bucket)``."""
        from couchbase.cluster import Cluster
        from couchbase.auth import PasswordAuthenticator
        from couchbase.options import ClusterOptions

        try:
            username = connection_details.get("username")
            password = connection_details.get("password")
            host = connection_details.get("host")
            port = int(connection_details.get("port", 8091))
            bucket_name = connection_details.get("bucket", "default")

            conn_str = f"couchbase://{host}" if port == 8091 else f"couchbase://{host}:{port}"

            auth = PasswordAuthenticator(username, password)
            options = ClusterOptions(auth)
            options.apply_profile("wan_development")
            cluster = Cluster(conn_str, options)
            bucket = cluster.bucket(bucket_name)

            logger.info("Couchbase connection established.")
            return cluster, bucket
        except Exception as e:
            logger.error("Couchbase connection failed: %s", e, exc_info=True)
            raise DataSourceException(f"Couchbase connection failed: {e}") from e

    def test_connection(self, connection: Any) -> bool:
        """Test Couchbase connection with N1QL fallback."""
        cluster, bucket = connection
        try:
            result = cluster.query("SELECT 1 as test")
            if bool(list(result)):
                return True
        except Exception:
            pass

        try:
            scopes = bucket.collections().get_all_scopes()
            return bool(scopes)
        except Exception:
            pass

        return False

    def parse_catalog(self, catalog: str, connection_details: Dict) -> Dict:
        """Parse catalog into bucket/scope/collection."""
        parts = catalog.split(".")
        bucket_name = connection_details.get("bucket", "default")

        if len(parts) == 1:
            return {"bucket": bucket_name, "scope": "_default", "collection": parts[0]}
        elif len(parts) == 2:
            return {"bucket": bucket_name, "scope": parts[0], "collection": parts[1]}
        elif len(parts) == 3:
            return {"bucket": parts[0], "scope": parts[1], "collection": parts[2]}
        else:
            return {"bucket": bucket_name, "scope": "_default", "collection": "_default"}

    def build_query(self, catalog_info: Dict, columns: List[str], limit: int) -> Dict:
        """Build N1QL SELECT query."""
        col_str = ", ".join(columns) if columns else "*"
        bucket = catalog_info["bucket"]
        scope = catalog_info["scope"]
        collection = catalog_info["collection"]

        if scope == "_default" and collection == "_default":
            query = f"SELECT {col_str} FROM `{bucket}` LIMIT {limit}"
        else:
            query = f"SELECT {col_str} FROM `{bucket}`.`{scope}`.`{collection}` LIMIT {limit}"

        return {"query": query}

    def execute_query(self, connection: Any, query_info: Dict) -> List[Dict]:
        """Execute N1QL query, return list of dicts."""
        cluster, _bucket = connection
        query_string = query_info["query"]
        try:
            result_set = cluster.query(query_string)
            return list(result_set)
        except Exception as e:
            logger.error("N1QL query failed: %s", e, exc_info=True)
            raise DataSourceException(f"Couchbase query execution failed: {e}") from e

    def get_metadata(self, connection: Any, connection_details: Dict) -> List[Dict]:
        """Retrieve scope/collection structure for UI tree."""
        _cluster, bucket = connection
        try:
            scopes = bucket.collections().get_all_scopes()
            metadata: List[Dict] = []

            for scope in scopes:
                scope_name = getattr(scope, "name", "Unknown")
                if scope_name == "_system":
                    continue

                scope_entry: Dict[str, Any] = {
                    "title": scope_name,
                    "value": scope_name,
                    "children": [],
                }

                collections = getattr(scope, "collections", []) or getattr(
                    scope, "_collections", []
                )
                for coll in collections:
                    coll_name = getattr(coll, "name", "Unknown")
                    if coll_name.startswith("_") and scope_name != "_default":
                        continue
                    scope_entry["children"].append(
                        {"title": coll_name, "value": f"{scope_name}.{coll_name}"}
                    )

                metadata.append(scope_entry)

            return metadata
        except Exception as e:
            logger.error("Couchbase metadata retrieval failed: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to get Couchbase metadata: {e}") from e

    def cleanup_connection(self, connection: Any) -> None:
        """Close Couchbase cluster connection."""
        if connection:
            cluster, _bucket = connection
            try:
                cluster.close()
                logger.info("Couchbase connection closed.")
            except Exception as e:
                logger.warning("Couchbase cleanup warning: %s", e)
