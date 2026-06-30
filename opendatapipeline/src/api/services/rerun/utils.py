import uuid
from ....models.connector import MongoConnector
from ....models.mongo.mongo_files import MongoFactory, MongoFiles
from ....etl.extract.file_operations.read import Read
from ....exceptions.exception import *
from ....logger.logger import Logger, logger
import random
import string
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase

mongo = MongoConnector()
read = Read()

mongo_client = mongo.client

class CreateDFDictionary:
    """Service for creating a dictionary of data frames from chat files.

    Retrieves file information from a chat document and creates a dictionary of data frames 
    based on feather files stored in a MongoDB collection.

    Attributes:
        session (Session): The database session used for operations.
        mongo_cache (MongoFiles): MongoDB factory for cache documents.

    Methods:
        create(chat_id):
            Creates and returns a dictionary of data frames for the given chat ID.
    """
    def __init__(self, session):
        """Initializes the CreateDFDictionary with a session and sets up the cache collection.

        Args:
            session (Session): The database session to use for operations.
        """
        self.session = session
        self.cache = get_cache(session=self.session)

    @Logger.generate
    def create(self, chat_id):
        """Creates a dictionary of data frames for the specified chat ID.

        Args:
            chat_id (str): The ID of the chat document to use for retrieving file information.

        Returns:
            dict: A dictionary where keys are source IDs and values are dictionaries containing
                  the data frame, alias, and file path.

        Raises:
            UtilsException: If an error occurs while creating data frames.
        """
        try:
            dataframes_dict = {}
            chats = MongoFactory(mongo_client, "chats", session=self.session)
            _, chat_document = chats.get_by_id(chat_id)
            user_id = chat_document["user_id"]
            for file_info in chat_document.get("files",[]):
                cache = self.cache.get_item(file_info["source_id"], user_id, chat_id)
                if cache is None:
                    # TODO: This makes pipeline execution very tightly coupled to data being already
                    #   present in cache, we need to improve it.
                    continue
                feather_file_path = cache.get("feather_file_path")
                file_name = cache.get("file_name")
                alias = cache.get("dataframe_alias",file_name)
                _, dataframe = read.feather(feather_file_path)
                dataframes_dict.update({file_info["source_id"]: {"df":dataframe, "alias":alias, "feather_file_path":feather_file_path}})
            
            return dataframes_dict
        except Exception as e:# pragma: no cover
            logger.error(f"Failed to create dataframes dictionaries due to {str(e)}.", exc_info=True)
            raise UtilsException(f"Failed to create dataframes dictionaries due to {str(e)}.") from e



class DFInformation:
    """Service for retrieving data frames and their configurations from a dictionary.

    Provides methods to retrieve data frames by source ID or alias and to get source IDs 
    based on aliases.

    Attributes:
        config_dict (dict): A dictionary containing data frame configurations where keys are source IDs.

    Methods:
        get(id=None, alias=None):
            Retrieves a data frame by its source ID or alias.

        get_id_by_alias(alias):
            Retrieves the source ID associated with a given alias.
    """
    def __init__(self, config_dict={}):
        """Initializes the DFInformation with a dictionary of data frame configurations.

        Args:
            config_dict (dict, optional): A dictionary of data frame configurations. Defaults to an empty dictionary.
        """
        self.config_dict = config_dict

    def get(self, id=None, alias=None):
        """Retrieves a data frame based on the provided source ID or alias.

        Args:
            id (str, optional): The source ID of the data frame to retrieve. Defaults to None.
            alias (str, optional): The alias of the data frame to retrieve. Defaults to None.

        Returns:
            DataFrame: The data frame corresponding to the provided source ID or alias.

        Raises:
            ValueError: If neither source ID nor alias is provided, or if the provided values do not match the configuration.
        """
        if not id and not alias:
            raise ValueError("Parameters need source_id or alias.")
        
        if id and alias:
            if id in self.config_dict:
                if self.config_dict[id]['alias'] == alias:
                    return self.config_dict[id]['df'].copy()
                else:
                    logger.error(
                        f"SourceId and alias mismatch. source_id and alias present - {[(i, v.get('alias')) for i, v in self.config_dict.items()]}, " +
                        f"source_id and alias requested - {(id, alias)}")
                    raise ValueError("Source ID and alias mismatch.")
            else:
                raise ValueError("The given alias or source_id is not registered.")
        
        if id:
            if id in self.config_dict:
                return self.config_dict[id]['df']
            else:
                raise ValueError("The given source_id is not registered.")
        
        if alias:
            matching_items = [value for key, value in self.config_dict.items() if isinstance(value, dict) and value.get('alias') == alias]
            if matching_items:
                return matching_items[0]['df'].copy()
            else:
                raise ValueError("The given alias is not registered.")
        
        raise Exception(f"Unexpected error with id: {id} and alias: {alias}")


    def get_id_by_alias(self, alias):
        """Retrieves the source ID associated with a given alias.

        Args:
            alias (str): The alias for which to find the source ID.

        Returns:
            str: The source ID associated with the given alias, or None if not found.
        """
        for key, value in self.config_dict.items():
            if value.get("alias") == alias:
                return key
        return None  # Return None if alias is not found

        
class ReRunUtilities:
    """Utilities for updating data frame configurations and generating random keys.

    Provides methods for updating data frame configurations based on aliases or source IDs, 
    and for generating random keys for new data frames.

    Methods:
        update_configurations(data_dict, alias=None, source_id=None, df=None, intent_name=None):
            Updates or adds new entries in the data frame dictionary based on the provided alias or source ID.

        generate_random_key(prefix):
            Generates a random key with a specified prefix.
    """
    def update_configurations(self, data_dict, alias=None, source_id=None, df=None, intent_name=None):
        """Updates or adds new entries in the data frame dictionary based on the provided alias or source ID.

        Args:
            data_dict (dict): The dictionary of data frame configurations to update.
            alias (str, optional): The alias of the data frame. Defaults to None.
            source_id (str, optional): The source ID of the data frame. Defaults to None.
            df (DataFrame, optional): The data frame to add or update. Defaults to None.
            intent_name (str, optional): The intent name used for generating a new alias if needed. Defaults to None.

        Returns:
            dict: The updated dictionary of data frame configurations.

        Raises:
            ValueError: If both alias and source ID are provided but do not match, or if neither is provided.
        """
        if not alias and not source_id:
            raise ValueError("Either alias or source_id must be provided.")

        if alias and source_id:
            # Check if alias or source_id already exist
            alias_exists = any(value["alias"] == alias for value in data_dict.values())
            source_id_exists = source_id in data_dict

            if source_id_exists and data_dict[source_id]["alias"] != alias:
                raise ValueError("Source ID and alias mismatch.")

            if not alias_exists and not source_id_exists:
                data_dict[source_id] = {"df": df, "alias": alias}
                return data_dict
            
            for key, value in data_dict.items():
                if key == source_id and value["alias"] == alias:
                    data_dict[key]["df"] = df
                    return data_dict

            raise ValueError("Source ID and alias mismatch.")
        
        if alias and not source_id:
            for key, value in data_dict.items():
                if value["alias"] == alias:
                    data_dict[key]["df"] = df
                    return data_dict
            # Alias not found, create new entry with random source_id
            new_source_id = str(uuid.uuid4())

            data_dict[new_source_id] = {"df": df, "alias": alias}
            return data_dict
        
        if source_id and not alias:
            if source_id in data_dict:
                data_dict[source_id]["df"] = df
                return data_dict
            # Source_id not found, create new entry with random alias
            new_alias = self.generate_random_key(intent_name)
            data_dict[source_id] = {"df": df, "alias": new_alias}
            return data_dict

    def generate_random_key(self,prefix):
        """Generates a random key with a specified prefix.

        Args:
            prefix (str): The prefix to use for the random key.

        Returns:
            str: A random key with the given prefix.
        """
        return prefix + '_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
