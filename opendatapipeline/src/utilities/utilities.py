import json
import yaml
from sqlalchemy.engine import URL

from ..exceptions.exceptions import UtilityException
from ..logger.logger import Logger, logger

from enum import Enum
import re
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
        
from ..models.connector import MongoConnector
from ..models.mongo.mongo_factory import MongoFactory
import pandas as pd
import io


mongo_client = MongoConnector()
mongo_client = mongo_client.client



class ReadFile: # pragma: no cover
    """
    Class for reading configuration files to extract connection URL information.

    This class provides methods to read YAML configuration files and extract connection
    details for different database engines. 

    :param None:
    :type None:
    :param yml_path: Path to the YAML configuration file to be read.
    :type yml_path: str
    :param engine: The database engine for which the connection URL is to be retrieved (e.g., 'mysql', 'postgres').
    :type engine: str
    :param connection_url_dict: Dictionary containing connection parameters (e.g., driver, username, password).
    :type connection_url_dict: dict
    :param catalog: The name of the catalog (table) from which data is to be fetched.
    :type catalog: str
    :param columns: List of columns to be selected in the query; if empty, selects all columns.
    :type columns: list of str
    :param engine: The database engine for which the query is to be constructed (e.g., 'mysql', 'postgres').
    :type engine: str
    :return: Dictionary containing connection string details for the specified engine, or SQL query strings.
    :rtype: dict or str
    :raises UtilityException: If the YAML file cannot be read, the specified engine is not found in the file, or the query cannot be generated.
    """
    @Logger.generate
    def get_connection_url_dict(self, yml_path, engine):
        """
        Reads a YAML configuration file and retrieves the connection URL dictionary for a specified database engine.

        :param yml_path: Path to the YAML configuration file.
        :type yml_path: str
        :param engine: The database engine for which the connection URL is to be retrieved (e.g., 'mysql', 'postgres').
        :type engine: str
        :return: Dictionary containing connection string details for the specified engine.
        :rtype: dict
        :raises UtilityException: If the YAML file cannot be read or the specified engine is not found in the file.
        """
        try:
            with open(yml_path, "r") as config_file:
                config = yaml.safe_load(config_file)
                logger.info("Successfully performed yml reader")
                for datasource in config['datasources']:
                    if datasource['driver'] == engine:
                        connection_url_dict = datasource['connection_string']
                return connection_url_dict
        except Exception as e: # pragma: no cover
            logger.error(f"Unable to perform yml reader with yml_path: {yml_path} and engine: {engine}", exc_info=True)
            raise UtilityException(f"Unable to perform yml reader: {str(e)}") from e
        
class CreateStrings: # pragma: no cover
    """
    Class for creating database connection strings and query strings.

    This class provides methods to generate connection strings and query strings for various database engines.

    :param connection_url_dict: Dictionary containing connection parameters (e.g., driver, username, password).
    :type connection_url_dict: dict
    :param engine: The database engine for which the connection string or query string is to be created (e.g., 'mysql', 'postgres').
    :type engine: str
    :param catalog: The name of the catalog (table) from which data is to be fetched.
    :type catalog: str
    :param columns: List of columns to be selected in the query; if empty, selects all columns.
    :type columns: list of str
    :return: Connection string or SQL query string based on the provided parameters.
    :rtype: str
    :raises UtilityException: If the connection URL or query cannot be generated for the specified engine.
    """
    @Logger.generate
    
    def create_connection_string(self, connection_url_dict, engine):
        """
        Generates a database connection string based on the provided dictionary and database engine.

        :param connection_url_dict: Dictionary containing connection parameters (e.g., driver, username, password).
        :type connection_url_dict: dict
        :param engine: The database engine for which the connection string is to be created (e.g., 'mysql', 'postgres').
        :type engine: str
        :return: A connection string for the specified database engine.
        :rtype: str
        :raises UtilityException: If the connection URL cannot be generated for the specified engine.
        """
        
        try:
            if engine in ["ms_sql_server", "oracle", "firebird", "mysql",'postgres']:
                if connection_url_dict.get('driver_name'):
                    connection_url = URL.create(connection_url_dict["driver"], username=connection_url_dict["username"], password=connection_url_dict["password"],
                                    host=connection_url_dict["host"], database=connection_url_dict["database"], port=connection_url_dict["port"],
                                    query={"driver": connection_url_dict['driver_name']})
                else:
                    connection_url = URL.create(connection_url_dict["driver"], username=connection_url_dict["username"], password=connection_url_dict["password"],
                                    host=connection_url_dict["host"], database=connection_url_dict["database"], port=connection_url_dict["port"])
            else:
                raise Exception(f"The engine is not supported {engine}")
            return connection_url  
        except Exception as e: # pragma: no cover
            logger.error(f"Failed to genererate connection url with connection_url_dict: {connection_url_dict} and engine: {engine}", exc_info=True)
            raise UtilityException(f"Failed to genererate connection url: {str(e)}") from e
        
    @Logger.generate
    def get_query_string(self, engine):
        """
        Retrieves the SQL query string to fetch the version of the database for the specified engine.

        :param engine: The database engine for which the version query is to be retrieved (e.g., 'mysql', 'postgres').
        :type engine: str
        :return: SQL query string to fetch the database version.
        :rtype: str
        :raises UtilityException: If the engine is not supported or the query cannot be generated.
        """
        try:
            # used because the select query varies from databases
            if engine == "ms_sql_server":
                query = "SELECT @@VERSION;"
            elif engine == "firebird":
                query = "SELECT rdb$get_context('SYSTEM', 'ENGINE_VERSION') FROM rdb$database;"
            elif engine == "oracle":
                query = "SELECT * FROM v$version"
            elif engine == "mysql":
                query = "SELECT VERSION()"
            elif engine == "postgres":
                query = "SELECT VERSION()"
            elif engine == "snowflake":
                query = "select current_version()"
            elif engine == "databricks":
                query = "SELECT current_catalog()"
            else:
                raise Exception(f"The engine is not supported {engine}")
            return query  
        except Exception as e: # pragma: no cover
            logger.error(f"Failed to get query with engine: {engine}", exc_info=True)
            raise UtilityException(f"Failed to get query: {str(e)}") from e
        
    @Logger.generate
    def get_fetch_data_string(self, engine, catalog, columns, num_rows=100):
        """
        Constructs an SQL query string to fetch data from a specified catalog with optional columns.

        :param engine: The database engine for which the query is to be constructed (e.g., 'mysql', 'postgres').
        :type engine: str
        :param catalog: The name of the catalog (table) from which data is to be fetched.
        :type catalog: str
        :param columns: List of columns to be selected in the query; if empty, selects all columns.
        :type columns: list of str
        :return: SQL query string to fetch data.
        :rtype: str
        :raises UtilityException: If the engine is not supported or the query cannot be generated.
        """
        # used because the select query varies from databases
        try:
            if columns != [] and columns != None:
                col = ", ".join(columns)
            else:
                col = "*"
            if engine == "ms_sql_server":
                query = f"SELECT TOP {num_rows} {col} FROM {catalog};"
            elif engine == "firebird":
                query = f"SELECT FIRST {num_rows} {col} FROM {catalog};"
            elif engine == "oracle":
                if col != "*":
                    col = ', '.join(f'"{col_value}"' for col_value in columns)
                schema, table = catalog.split('.')
                catalog_value = f'"{schema.lower()}"."{table.upper()}"'
                query = f'SELECT {col} FROM {catalog_value} FETCH FIRST {num_rows} ROWS ONLY'
            elif engine == "mysql":
                query =  f"SELECT {col} FROM {catalog} LIMIT {num_rows}"
            elif engine == "postgres":
                query =  f"SELECT {col} FROM {catalog} LIMIT {num_rows}"
            elif engine == "snowflake":
                query =  f"SELECT {col} FROM {catalog} LIMIT {num_rows}"
            elif engine == "databricks":
                query =  f"SELECT {col} FROM {catalog} LIMIT {num_rows}"
            else:
                raise Exception(f"The engine is not supported {engine}")
            return query
        except Exception as e: # pragma: no cover
            logger.error(f"Failed to get query with engine: {engine}, catalog: {catalog} and columns: {columns}", exc_info=True)
            raise UtilityException(f"Failed to get query: {str(e)}") from e


class CommonUtils: # pragma: no cover
    @Logger.generate
    def replace_special_chars(self, file_name):
    # Replace all non-alphanumeric characters with underscores
        sanitized_filename = re.sub(r'[^A-Za-z0-9_.]', '_', file_name)
        return sanitized_filename

    def get_chat_files_aliases_document(self, session,chat_id):
        try:
            chats = MongoFactory(mongo_client, "chats", session=session)
            cache: CacheBase = get_cache(session=session)
            status, chat = chats.get_by_id(chat_id)

            loaded_files = []
           
            for file in chat.get("files", []):
                data = {}
                cache_file = cache.get_item(file.get("source_id"), chat["user_id"], chat_id)
                if cache_file:
                    file_name = cache_file.get("file_name")
                    data["alias"] = cache_file.get("dataframe_alias", file_name)
                    data["type"] = cache_file.get("type")
                    data["source_id"] = file.get("source_id") 
                    data["_id"] = cache_file.get("source_db_object_id")
                    loaded_files.append(data)
                else:
                    loaded_files.append(file)
            return loaded_files
        except Exception as e:
            logger.error(f"Failed to get chat file alias document - {e}")
            return []
        
    def get_unique_name(self,name, data):
        try:
            aliases = [item["alias"] for item in data]
            while name in aliases:
                    name=f"{name}_copy"
            return name
        except Exception as e:
            return name
        
        
    def replace_alias_in_history(self,history, old_alias, new_alias):
        try:
            def replace_in_dict(d, old, new):
                
                """
                Replace old alias with new alias in a dictionary's string values.
                """
                # Compile regex pattern with word boundaries for exact match
                pattern = re.compile(r'\b' + re.escape(old) + r'\b')
                
                for key, value in d.items():
                    if key in ["output", "parameters", "dataframe_alias"]:
                        if isinstance(value, str):
                            # Replace exact matches of old_alias with new_alias
                            d[key] = pattern.sub(new, value)
                        elif isinstance(value, dict):
                            d[key] = replace_in_dict(value, old, new)
                        elif isinstance(value, list):
                            d[key] = [replace_in_dict(item, old, new) if isinstance(item, dict) else pattern.sub(new, item) if isinstance(item, str) else item for item in value]
                return d

            # Replace old alias with new alias in each dictionary in the history list
            updated_history = [replace_in_dict(item, old_alias, new_alias) for item in history]
            return updated_history
        except Exception as e:
            raise Exception("Failed to Rename!") from e
            
    def get_cwf_alias(self,session,chat_id):
        try:
            chats = MongoFactory(mongo_client, "chats", session=session)
            cache: CacheBase = get_cache(session=session)
        
            status,chat =chats.get_by_id(chat_id)
            cwf = chat.get("cwf") #{"source_id" : "34567890987654"}
            
            source_id = cwf.get("source_id")
            if source_id:
                cache = cache.get_item(source_id, chat["user_id"], chat_id)
                file_name = cache.get("file_name")
                alias = cache.get("dataframe_alias",file_name)
                return alias
        except Exception as e:
            return ""
        
    def check_and_add_alias(self,text_input, current_working_alias, all_files):
    # Extract aliases from the all files
        all_aliases = {file['alias'] for file in all_files}
        
        # Check if any alias from the list matches in the text input
        matched_aliases = [alias for alias in all_aliases if alias in text_input]
        
        if matched_aliases:
            return ""

        else:
            return current_working_alias
            # Add the current working alias to the result

    def extract_steps(text):
        """Extracts steps blocks from the given text"""
        generic_pattern = r'<steps>(.*?)</steps>'
        generic_match = re.search(generic_pattern, text, re.DOTALL)
        if generic_match:
            return generic_match.group(1).strip()

        # No code block found
        return None

    def get_excel_sheetnames_from_s3(self, s3_client, bucket: str, key: str):
        try:
            response = s3_client.get_object(Bucket=bucket, Key=key)
            file_bytes = response["Body"].read()

            # Use pandas to read Excel sheet names
            excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
            return excel_file.sheet_names

        except Exception as e:
            logger.error(f"Failed to read Excel sheet names from S3 file {key}: {e}")
            return []
    
    def build_tree_from_s3_keys(self, s3_keys, s3_client, s3_bucket):
        tree = {}
        for key in s3_keys:
            parts = key.strip("/").split("/")
            current_level = tree
            for i, part in enumerate(parts):
                is_last = i == len(parts) - 1

                # If key ends with '/' and has only 1 part like 'test/', it's a folder
                if len(parts) == 1 and key.endswith("/"):
                    is_last = False

                part_path = "/".join(parts[:i + 1])
                if part_path not in current_level:
                    node_type = "folder"
                    children = {} if not is_last else None
                    #title = part + ("/" if not is_last else "")
                    #value = part_path if is_last else part_path + "/"

                    if is_last:
                        extension_parts = part.rsplit(".", 1)
                        filename = extension_parts[0]
                        ext = extension_parts[-1].lower() if len(extension_parts) == 2 else "file"
                        node_type = ext

                        if ext in ["xlsx", "xls"]:
                            children = []
                            try:
                                logger.debug(f"Fetching Excel file from S3: {key}")
                                sheet_names = self.get_excel_sheetnames_from_s3(s3_client, s3_bucket, key)
                                for sheet_name in sheet_names:
                                    children.append({
                                        "title": sheet_name,
                                        "value": f"{part_path}.{sheet_name}",
                                        "type": "sheet"
                                    })
                            except Exception as e:
                                logger.warning(f"Failed to load Excel sheet names for '{key}': {str(e)}")

                    current_level[part_path] = {
                        "title": part + ("/" if not is_last else ""),
                        "value": part_path if is_last else part_path + "/",
                        "type": node_type,
                        "children": children
                    }

                if not is_last:
                    current_level = current_level[part_path]["children"]

        def convert_to_list(node_dict):
            result = []
            for node in node_dict.values():
                if node["type"] == "folder":
                    node["children"] = convert_to_list(node["children"])
                    if not node["children"]:  # Skip empty folders
                        continue
                result.append(node)
            return result

        return convert_to_list(tree)


class ReadUtils:
    def map_columns(self, df):
        columns = [re.sub('[^0-9a-zA-Z]+', '_', col) for col in map(str.lower, df.columns)]
        return columns
    

class DocumentDBUtils:
    def _flatten_document(self, doc, prefix="", max_depth=3, current_depth=0):
        """
        Recursively flattens nested JSON into flat dict using DOT NOTATION for DataFrame compatibility.
        
        Updated to use dot notation instead of underscores to resolve column name ambiguity.
        
        Args:
            doc: Document to flatten (dict/list/primitive)
            prefix (str): Key prefix for nested fields (using dot notation)
            max_depth (int): Max recursion depth to prevent overflow
            current_depth (int): Current recursion level
            
        Returns:
            dict: Flattened key-value pairs with dot-separated keys
            
        Examples:
            {"user": {"name": "John"}} -> {"user.name": "John"}
            {"user_profile": "data"} -> {"user_profile": "data"} (preserved as-is)
            {"tags": ["a", "b"]} -> {"tags": "a, b"}
        """
        flattened = {}  # Result dictionary
        
        # Prevent infinite recursion by checking depth
        if current_depth >= max_depth:
            if prefix:
                key = prefix.rstrip('.')  # Clean prefix (remove trailing dot)
                # Convert deep structures to JSON strings
                flattened[key] = json.dumps(doc) if isinstance(doc, (dict, list)) else str(doc)
            return flattened
        
        # Process dictionary objects recursively
        if isinstance(doc, dict):
            for key, value in doc.items():
                # Build nested key using DOT notation instead of underscore
                new_key = f"{prefix}{key}" if prefix else key  # Build nested key
                
                if isinstance(value, dict):
                    # Recursive call for nested objects using DOT separator
                    nested = self._flatten_document(value, f"{new_key}.", max_depth, current_depth + 1)
                    flattened.update(nested)  # Merge nested results
                elif isinstance(value, list):
                    # Handle arrays based on content type
                    if value and isinstance(value[0], dict):
                        # Array of objects -> JSON string
                        flattened[new_key] = json.dumps(value)
                    else:
                        # Array of primitives -> CSV string for UI
                        flattened[new_key] = ", ".join(str(item) for item in value)
                else:
                    # Store primitive values directly
                    flattened[new_key] = value
        else:
            # Handle non-dict documents
            key = prefix.rstrip('.') if prefix else 'value'
            flattened[key] = doc
        
        return flattened

    def _normalize_dataframe_types(self, dataframe):
        """
        Normalizes DataFrame types for mixed schema compatibility.
        
        Args:
            dataframe (pandas.DataFrame): Input with mixed types
            
        Returns:
            pandas.DataFrame: Normalized with consistent types
            
        Process:
            - Object columns -> strings with null preservation
            - Numeric columns -> unchanged (pandas handles nulls)
            - 'nan' strings -> pandas.NA
            
        """
        try:
            
            # Process each column individually
            for column in dataframe.columns:
                if dataframe[column].dtype == 'object':
                    # Handle object columns with mixed types
                    non_null_values = dataframe[column].dropna()  # Get non-null values
                    
                    if len(non_null_values) > 0:
                        # Convert to strings for consistency
                        dataframe[column] = dataframe[column].astype(str)
                        # Replace string 'nan' with proper pandas.NA
                        dataframe[column] = dataframe[column].replace('nan', pd.NA)
                
                elif dataframe[column].dtype in ['int64', 'float64']:
                    # Keep numeric columns unchanged - pandas handles nulls well
                    pass
            logger.info(f"Dataframe from normalize_dataframe_types {dataframe}")
            return dataframe
            
        except Exception as e:
            # Return original on failure
            logger.warning(f"Type normalization failed: {e}")
            return dataframe

    def _resolve_column_conflicts(self, dataframe):
        """
        Resolve column name conflicts using suffix numbering strategy.
        
        Ensures pandas-Spark consistency by applying identical conflict resolution.
        
        Args:
            dataframe (pandas.DataFrame): DataFrame with potentially conflicting column names
            
        Returns:
            pandas.DataFrame: DataFrame with resolved column names
        """
        original_columns = list(dataframe.columns)
        resolved_columns = []
        column_counts = {}
        conflicts_detected = []
        
        # Process each column name for conflicts
        for col in original_columns:
            if col in column_counts:
                # Conflict detected - apply suffix numbering
                column_counts[col] += 1
                resolved_name = f"{col}_{column_counts[col]}"
                conflicts_detected.append({
                    'original': col,
                    'resolved': resolved_name,
                    'occurrence': column_counts[col]
                })
            else:
                # First occurrence - use original name
                column_counts[col] = 0
                resolved_name = col
            
            resolved_columns.append(resolved_name)
        
        # Apply resolved column names
        dataframe.columns = resolved_columns
        
        # Log conflicts if any were detected
        if conflicts_detected:
            logger.warning(f"Resolved {len(conflicts_detected)} column name conflicts using suffix numbering")
            for conflict in conflicts_detected:
                logger.debug(f"  {conflict['original']} -> {conflict['resolved']}")
        
        return dataframe
