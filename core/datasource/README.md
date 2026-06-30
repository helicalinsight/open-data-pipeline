# Core Datasource Components

This package contains the core components for data source connectivity: `DBConnection` (abstract base), `DataSourceConnector` (factory), and shared utilities.

## DBConnection

`DBConnection` is an abstract base class that every data source connector must implement.

### Design
- **Abstract Base Class:** Requires subclasses to implement `connect()`, `test_connection()`, `fetch_data()`, `get_metadata()`, and `get_columns()`.
- **Optional Engine Methods:** RDBMS connectors should also override `get_connection_string()` and `get_engine()` to support SQLAlchemy-based workflows (e.g., dlt pipelines).

### Usage
```python
from core.datasource.base import DBConnection

class MyDBConnector(DBConnection):
    def connect(self, connection_details, engine=None):
        ...
    def test_connection(self, connection_details, engine=None, connection=None):
        ...
    def fetch_data(self, connection_details, catalog, columns=[], engine=None, connection=None, num_rows=100):
        ...
    def get_metadata(self, connection_details, engine=None, connection=None):
        ...
    def get_columns(self, connection_details, db_table_name, engine=None, connection=None):
        ...
    # Optional for RDBMS connectors:
    def get_connection_string(self, connection_details):
        ...
    def get_engine(self, connection_details, **pool_kwargs):
        ...
```

## DataSourceConnector (Factory)

`DataSourceConnector` maps source type strings to their concrete implementations and uses lazy imports to avoid loading unnecessary dependencies.

### Usage
```python
from core.datasource.connector import DataSourceConnector

connector = DataSourceConnector()

# Create a connector by type
db = connector.create("postgres")

# Use the connector
engine = db.get_engine(connection_details)
conn_string = db.get_connection_string(connection_details)
metadata = db.get_metadata(connection_details, engine=engine)
```

### Supported Types
`astra`, `cassandra`, `firebird`, `mysql`, `postgres`, `redshift`, `snowflake`, `oracle`, `ms_sql_server`, `google_sheets`, `s3`, `couchbase`, `databricks`

### Extending with Custom Types
```python
connector = DataSourceConnector()
connector.register("my_db", "myapp.connectors.my_db", "MyDBConnection")
db = connector.create("my_db")
```

## DataSourceException

Base exception class for all datasource-related errors. Drop-in replacement for `DatabaseConnectorException`.

```python
from core.datasource.exceptions import DataSourceException

raise DataSourceException("Connection failed")
```

## Shared Utilities (`utils.py`)

- `map_columns(df)` — Sanitise DataFrame column names (lowercase + alphanumeric only)
- `build_tree_from_s3_keys(keys, client, bucket)` — Build hierarchical tree from S3 keys
- `CreateStrings` — SQL query builder helpers (connection strings, version queries, data fetch queries)
- `DocumentDBUtils` — Couchbase/DocumentDB document flattening and DataFrame normalization
