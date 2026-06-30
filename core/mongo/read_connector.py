# mongo_utils.py

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, AutoReconnect, NetworkTimeout
import logging
import os
import threading
import time
import random
from core.mongo.config import MongoConfig

logging.basicConfig(level=logging.DEBUG)

class ReadMongoConnector:
    """
    Thread-safe singleton class to handle the connection to a MongoDB instance.

    This class ensures that only one instance of MongoConnector is created (singleton pattern) and
    provides methods to connect to and interact with a MongoDB database.

    Attributes:
        _instance: The singleton instance of the MongoConnector class.
        _lock: Thread lock for thread-safe singleton creation.
        _client: MongoDB client instance connected to the specified database.
        _config: Configuration settings used for MongoDB connection.

    :param None:
    :type None:
    :return: The singleton instance of MongoConnector.
    :rtype: MongoConnector
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """
        Creates a new instance of MongoConnector if it doesn't already exist.
        Ensures that only one instance of MongoConnector is created (thread-safe singleton pattern).

        :return: The singleton instance of MongoConnector.
        :rtype: MongoConnector
        """
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking pattern for thread safety
                if cls._instance is None:
                    cls._instance = super(ReadMongoConnector, cls).__new__(cls)
                    cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        """
        Initialize the MongoDB connection and configuration.
        This method is called only once during singleton creation.
        """
        self._config = MongoConfig.config
        self._client = None
        self._client = self._connect_to_mongo()

    def _connect_to_mongo(self):
        """
        Establishes a connection to MongoDB using the configuration settings.

        :return: The MongoDB database instance.
        :rtype: pymongo.database.Database
        :raises ValueError: If the connection to MongoDB fails.
        """
        try:
            logging.info('Connecting to MongoDB')
            
            # Validate required configuration
            if not self._config or 'mongo' not in self._config:
                raise ValueError("MongoDB configuration not found")
            
            port = self._config['mongo'].get("port")
            host = self._config['mongo'].get('host')
            database_name = self._config['mongo'].get('database')
            username = self._config['mongo'].get('username')
            password = self._config['mongo'].get('password', os.environ.get('MONGO_PASSWORD'))
            
            # Validate required fields
            if not all([host, database_name, username, password]):
                raise ValueError("Missing required MongoDB configuration: host, database, username, or password")
            
            # Support for replica set with multiple hosts
            replica_set_name = self._config['mongo'].get('replica_set', 'rs0') # 'rs0' replica_set is used usually in local setup, 'askOnDataReplicaSet' is used in dev and prod
            
            # Parse host configuration - support both single host and comma-separated list
            if ',' in host:
                # Multiple hosts for replica set (comma-separated)
                hosts = [h.strip() for h in host.split(',')]
                hosts_with_port = []
                for h in hosts:
                    if port and ":" not in h:
                        hosts_with_port.append(f"{h}:{port}")
                    else:
                        hosts_with_port.append(h)
                hosts_str = ",".join(hosts_with_port)
                connection_string = f"mongodb://{username}:{password}@{hosts_str}/?authMechanism=DEFAULT&authSource={database_name}&replicaSet={replica_set_name}"
                logging.info('Connecting to MongoDB replica set: %s', replica_set_name)
            else:
                # Single host (backward compatibility)
                if port:
                    connection_string = f"mongodb://{username}:{password}@{host}:{port}/?authMechanism=DEFAULT&authSource={database_name}"
                else:
                    connection_string = f"mongodb://{username}:{password}@{host}/?authMechanism=DEFAULT&authSource={database_name}"
                logging.info('Connecting to MongoDB single host')
            
            logging.info('Connection string: %s', connection_string)

            max_attempts = int(os.environ.get('MONGO_CONNECT_MAX_ATTEMPTS', 5))
            base_delay = float(os.environ.get('MONGO_CONNECT_BASE_DELAY_SECONDS', 0.5))

            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    client = MongoClient(
                        connection_string,
                        maxPoolSize=50,
                        minPoolSize=10,
                        maxIdleTimeMS=30000,
                        maxConnecting=2,
                        serverSelectionTimeoutMS=10000,
                        connectTimeoutMS=10000,
                        socketTimeoutMS=30000,
                        retryWrites=True,
                        retryReads=True,
                        w='majority',
                        readPreference='primaryPreferred'
                    )
                    client.admin.command('ping')
                    server_info = client.server_info()
                    logging.info('Connected to MongoDB version: %s', server_info.get("version", "unknown"))
                    logging.info('App environment: %s', os.environ.get("APP_ENVIRONMENT", "unknown"))
                    logging.info('MongoDB connection established successfully!')
                    return client[database_name]
                except (ServerSelectionTimeoutError, ConnectionFailure, AutoReconnect, NetworkTimeout) as e:
                    last_exception = e
                    if attempt == max_attempts:
                        break
                    sleep_s = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                    logging.warning('Mongo connect attempt %s/%s failed: %s. Retrying in %.2fs', attempt, max_attempts, str(e), sleep_s)
                    time.sleep(sleep_s)
                except Exception as e:
                    last_exception = e
                    if attempt == max_attempts:
                        break
                    sleep_s = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                    logging.warning('Mongo unexpected error on attempt %s/%s: %s. Retrying in %.2fs', attempt, max_attempts, str(e), sleep_s)
                    time.sleep(sleep_s)

            if isinstance(last_exception, ServerSelectionTimeoutError):
                logging.error("Server selection timeout: %s", str(last_exception))
                raise ValueError(f"Server selection timeout: {str(last_exception)}") from last_exception
            if isinstance(last_exception, ConnectionFailure):
                logging.error("Failed to connect to MongoDB: %s", str(last_exception))
                raise ValueError(f"Failed to connect to MongoDB: {str(last_exception)}") from last_exception
            logging.error("Unexpected error connecting to MongoDB: %s", str(last_exception))
            raise ValueError(f"Unexpected error connecting to MongoDB: {str(last_exception)}") from last_exception
            
        except ServerSelectionTimeoutError as e:
            logging.error("Server selection timeout: %s", str(e))
            raise ValueError(f"Server selection timeout: {str(e)}") from e
        except ConnectionFailure as e:
            logging.error("Failed to connect to MongoDB: %s", str(e))
            raise ValueError(f"Failed to connect to MongoDB: {str(e)}") from e
        except Exception as e:
            logging.error("Unexpected error connecting to MongoDB: %s", str(e))
            raise ValueError(f"Unexpected error connecting to MongoDB: {str(e)}") from e

    @property
    def client(self):
        """
        Provides access to the MongoDB client instance.

        :return: The MongoDB client instance.
        :rtype: pymongo.database.Database
        """
        if self._client is None:
            raise ValueError("MongoDB connection not initialized")
        try:
            self._client.command('ping')
        except Exception as e:
            logging.warning('MongoDB ping failed (%s). Reconnecting...', str(e))
            self._client = self._connect_to_mongo()
        return self._client

    @classmethod
    def get_connection_stats(cls):
        """
        Get connection pool statistics for monitoring.
        
        :return: Dictionary with connection statistics.
        :rtype: dict
        """
        if cls._instance and cls._instance._client:
            try:
                # Access the underlying MongoClient
                mongo_client = cls._instance._client._Database__client
                return {
                    'active_connections': len(mongo_client._topology._servers),
                    'pool_size': getattr(mongo_client, 'max_pool_size', 'unknown'),
                    'server_info': mongo_client.server_info()
                }
            except Exception as e:
                return {'error': str(e)}
        return {'error': 'No connection available'}

    def health_check(self):
        """
        Perform a health check on the MongoDB connection.
        
        :return: True if connection is healthy, False otherwise.
        :rtype: bool
        """
        try:
            if self._client is None:
                return False
            
            # Simple ping to check connection health
            self._client.command('ping')
            return True
        except Exception as e:
            logging.error("Health check failed: %s", str(e))
            return False
