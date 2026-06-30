
# Core Mongo Components

This package contains the core components for MongoDB interaction: `MongoConnector` and `MongoFactory`.

## MongoConnector

`MongoConnector` is an abstract Singleton class designed to manage the MongoDB connection. It handles connection pooling, retry logic, and configuration access in a unified way.

### Design
- **Singleton Pattern:** Ensures only one `MongoClient` instance exists per application lifecycle.
- **Abstract Base Class:** Requires subclasses to implement `_get_config()` to provide environment-specific configuration.
- **Connection Management:** Handles replica set connections, password retrieval (config or env var), and connection pooling.

### Usage
To use `MongoConnector`, create a subclass in your application's model layer and implement `_get_config`.

**Example:**
```python
from core.mongo.connector import MongoConnector as CoreMongoConnector
from myapp.config import Config

class MongoConnector(CoreMongoConnector):
    def _get_config(self):
        return Config.config

# Instantiation
connector = MongoConnector()
db = connector.client # Returns the pymongo Database object
```

## MongoFactory

`MongoFactory` is a wrapper class for MongoDB collection operations. It provides a consistent interface for common operations like `find`, `aggregate`, `insert`, etc., with built-in logging and error handling.

### Design
- **Collection Wrapper:** initialized with a MongoDB Database object and a collection name.
- **Session Support:** specific operations can use a `ClientSession` for transactions.
- **Standardized Logging:** Uses the core logger to log operations and errors.

### Usage
Instantiate `MongoFactory` with a database object (obtained from `MongoConnector`) and the target collection name.

**Example:**
```python
class MyService:
    def __init__(self):
        self.client = MongoConnector().client
        self.users = MongoFactory(self.client, "users")

    def get_active_users(self):
        return self.users.find({"status": "active"})
```

### Key Methods
- `find(query)`: Returns a cursor for matching documents.
- `aggregate(pipeline)`: Performs an aggregation pipeline.
- `get_by_id(_id)`: Fetches a document by its MongoDB ObjectId.
