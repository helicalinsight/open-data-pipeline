from .astra import Astra
from .cassandra import Cassandra
from .firebird import Firebird
from .googlesheet import GoogleSheet
from .mysql import MySQL
from .postgres import Postgres
from .redshift import Redshift
from .snowflake import Snowflake
from .sqlserver import SQLServer
from .oracle import Oracle
from .s3 import S3
from .couchbase import Couchbase
from .databricks import Databricks

from ..logger.logger import Logger, logger
from ..exceptions.exceptions import *
logger = Logger

class DatabaseProvider:
    collection_mapping = {
        "astra": Astra,
        "cassandra": Cassandra,
        "firebird": Firebird,
        "google_sheets": GoogleSheet,
        "mysql": MySQL,
        "postgres": Postgres,
        "redshift": Redshift,
        "snowflake": Snowflake,
        "sqlserver": SQLServer,
        "oracle": Oracle,
        "s3": S3,
        "couchbase":Couchbase,
        "databricks": Databricks
    }

    @staticmethod
    @logger.generate
    def create_object(collection, spark):
        try:
            logger.debug("Creating db object..")
            logger.debug(f"The database collection is {collection}")
            collection = DatabaseProvider.collection_mapping.get(collection)            
            logger.debug("Returning db object..")
            return collection(spark)
        except Exception as e:
            logger.error(f"Error while creating db object: {str(e)}")
            raise UtilsException("Failed to create object.") from e
