import configparser
import os
from typing import Dict, Any

class MongoConfig:
    """
    Configuration class for MongoDB.
    Loads configuration from ini files based on the APP_ENVIRONMENT environment variable.
    """
    config = configparser.ConfigParser()
    
    # Determine the configuration file based on the environment
    environment = os.getenv("APP_ENVIRONMENT", "local")
    
    if environment == "prod":
        config_file = os.path.join(os.path.dirname(__file__), "configs", "mongo-config-prod.ini")
    elif environment == "dev":
        config_file = os.path.join(os.path.dirname(__file__), "configs", "mongo-config-dev.ini")
    else:
        config_file = os.path.join(os.path.dirname(__file__), "configs", "mongo-config-local.ini")
        
    if os.path.exists(config_file):
        config.read(config_file)
    else:
        # Fallback or error logging if needed, though typically we expect the file to exist
        print(f"Warning: Mongo config file not found at {config_file}")

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        Returns the raw config parser object or a dictionary. 
        Current usage expects the config parser object which has dict-like access.
        """
        return cls.config
