
import uuid
import pandas as pd
import os
import json

from .utils import get_unique_name
from abc import ABC, abstractmethod

# Patch for Pandas 2.x to restore 'iteritems' method for PySpark compatibility
# Since 'iteritems' was removed in Pandas 2.0, this patch ensures that PySpark can still function
# correctly with Pandas DataFrames by using the 'items' method as a fallback.
if not hasattr(pd.DataFrame, "iteritems"):
    pd.DataFrame.iteritems = pd.DataFrame.items
    
# ENGINE-INDEPENDENT CLASSES 
class JobArguments:
    def __init__(self, config_dict={}):
        self.config_dict = config_dict

    def get(self, config_name=None):
        try:
            if config_name:
                return {config_name: self.config_dict[config_name]}
            else:
                return self.config_dict
        except Exception as e:
            raise Exception(str(e)) from e
    
    def create(self, config_name, config_value):
        try:
            if config_name in list(self.config_dict.keys()):
                raise Exception(f"The key {config_name} already exists, please use a different key.")
            self.config_dict.update({config_name:config_value})
            return self.config_dict
        except Exception as e:
            raise Exception(str(e)) from e

    def update(self, config_name, config_value):
        try:
            self.config_dict.update({config_name:config_value})
            return self.config_dict
        except Exception as e:
            raise Exception(str(e)) from e

    def delete(self, config_name):
        try:
            self.config_dict.pop(config_name)
            return self.config_dict
        except Exception as e:
            raise Exception(str(e)) from e


class Connection:
    def __init__(self, connection_id_dict=None):
        if connection_id_dict is None:
            connection_id_dict = {}
        self.connection_id_dict = connection_id_dict
        self.connection_by_file, self.connection_by_source_name = self._parse_connection_dict(self.connection_id_dict)

    def _parse_connection_dict(self, connection_dict):
        file_dict, source_dict = {}, {}

        for key, value in connection_dict.items():
            if value['type'] == 'file':
                file_dict[value['details']['file_name']] = {
                    "file_id": key,
                    "file_name": value['details']['file_name'],
                    "file_type": value['details']['file_type'],
                    "full_name": value['details']['full_name']
                }
                
            elif value['type'] == 'database':
                source_name = value.get('details', {}).get('sourceName')
                if not source_name:
                    source_name = value.get('details', {}).get('source_name')
                if not source_name:
                    continue
                source_dict[source_name] = {
                    'connection_id': key,
                    'host': value['details'].get('host', ''),
                    'port': value['details'].get('port', ''),
                    'user': value['details'].get('user', value['details'].get('username')),
                    'password': value['details'].get('password'),
                    'database': value['details'].get('database'),
                    'dbtype': value['details'].get('type', '')
                }
       
        return file_dict, source_dict

    def get_by_file_name(self, file_name):
        if file_name not in self.connection_by_file:
            raise ValueError(f"No connection found with file name {file_name}")
        return self.connection_by_file[file_name]

    def get_by_source_name(self, source_name):
        if source_name not in self.connection_by_source_name:
            raise ValueError(f"No connection found with source name {source_name}")
        return self.connection_by_source_name[source_name]

    def get(self, id):
        return self.connection_id_dict.get(id, None)
    
    def items(self):
        return self.connection_id_dict.items()
    
    def keys(self):
        return self.connection_id_dict.keys()


# PARENT CLASSES 

class ReadOrWriteFiles(ABC):
    """Abstract parent class with common file operations logic"""
    
    def __init__(self, user_id, basepath):
        self.user_id = user_id
        self.basepath = basepath
        

    def create_file_path(self, file_name):
        """Common file path creation logic"""
        try:
            file_path = os.path.join("/",self.basepath,"upload",self.user_id, "sources", "flat_files", file_name)
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            return file_path
        except Exception as e:
            raise Exception(str(e)) from e

    def read_json(self, file_name, **kwargs):
        """Common JSON reading logic"""
        try:
            file_path = self.create_file_path(file_name)
            with open(file_path, 'r') as json_file:
                json_data = json.load(json_file)
            return json_data
        except Exception as e:
            raise Exception(str(e)) from e
        
    def write_json(self, file_name, json_data, **kwargs):
        """Common JSON writing logic"""
        try:
            file_path = self.create_file_path(file_name)
            with open(file_path, 'w') as json_file:
                json.dump(json_data, json_file, indent=4, **kwargs) 
            return True             
        except Exception as e:
            raise Exception(f"Error writing JSON to file: {str(e)}") from e

    @abstractmethod
    def read_csv(self, engine, file_name, **kwargs):
        """To be overridden by child classes"""
        raise NotImplementedError("Subclass must implement read_csv")
        
    @abstractmethod
    def read_excel(self, engine, file_name, **kwargs):
        """To be overridden by child classes"""
        raise NotImplementedError("Subclass must implement read_excel")
        
    @abstractmethod
    def write_csv(self, engine, file_name, dataframe, **kwargs):
        """To be overridden by child classes"""
        raise NotImplementedError("Subclass must implement write_csv")
        
    @abstractmethod
    def write_excel(self, engine, file_name, dataframe, **kwargs):
        """To be overridden by child classes"""
        raise NotImplementedError("Subclass must implement write_excel")


class DataframeInformation(ABC):
    """Abstract parent class with common DataFrame information logic"""
    
    def __init__(self, config_dict={}):
        self.config_dict = config_dict

    def get(self, id=None, alias=None):
        """Common get logic"""
        try:
            if id and alias:
                if id in self.config_dict and self.config_dict[id].get('alias') == alias:
                    return self.config_dict[id]["df"]
                else:
                    raise Exception(f"ID '{id}' and Alias '{alias}' are either not registered or mismatched.")
            
            elif id:
                if id in self.config_dict:
                    return self.config_dict[id]["df"]
                else:
                    raise Exception(f"ID '{id}' not found.")
            
            elif alias:
                id = next((key for key, value in self.config_dict.items() if isinstance(value, dict) and value.get('alias') == alias), None)
                if id:
                    return self.config_dict[id]["df"]
                else:
                    raise Exception(f"Alias '{alias}' not found.")
            
            else:  # if id is None and alias is None
                return self.config_dict
        
        except Exception as e:
            raise Exception(str(e)) from e
    
    def create(self, dataframe, alias=None, id=None):
        """Common create logic"""
        try:
            id_exists = False
            if id and id in self.config_dict:
                id_exists = True
                # Check if alias is already assigned to another id
                for key, value in self.config_dict.items():
                    if isinstance(value, dict):
                        if value.get('alias') == alias and key != id:
                            raise Exception(f"The alias '{alias}' is already assigned to another ID.")
            
            alias_exists = next((key for key, value in self.config_dict.items() if isinstance(value, dict) and value.get('alias') == alias), None)

            if alias_exists or id_exists:
                self.delete(alias)
                    
            if not id:
                id = str(uuid.uuid4())
            self.config_dict[id] = {"df": dataframe, "alias": alias}
            data = {
                "source_id": id,
                "alias": alias
            }
            return data
        except Exception as e:
            raise Exception(str(e)) from e

    def update(self, alias, dataframe, id=None):
        """Common update logic"""
        try:
            if id and alias:
                # Check if id and alias match as a key-value pair
                if self.config_dict.get(id, {}).get('alias') != alias:
                    raise Exception(f"ID '{id}' and Alias '{alias}' do not match.")
                else:
                    self.config_dict[id]['df'] = dataframe
                    return True

            # Find id based on alias
            id = next((key for key, value in self.config_dict.items() if isinstance(value, dict) and value.get('alias') == alias), None)
            if not id:
                raise Exception(f"Alias '{alias}' is not registered.")

            # Update dataframe
            self.config_dict[id]['df'] = dataframe
            return True

        except Exception as e:
            raise Exception(str(e)) from e

    def delete(self, alias, id=None):
        """Common delete logic"""
        try:
            if id and alias:
                # Check if id and alias match as a key-value pair
                if self.config_dict.get(id, {}).get('alias') != alias:
                    raise Exception(f"ID '{id}' and Alias '{alias}' do not match.")
                else:
                    self.config_dict.pop(id)
                    return True
            
            # Find id based on alias
            id = next((key for key, value in self.config_dict.items() if isinstance(value, dict) and value.get('alias') == alias), None)
            if not id:
                raise Exception(f"Alias '{alias}' is not registered.")
            
            # Remove entry from config_dict
            self.config_dict.pop(id)
            return True

        except Exception as e:
            raise Exception(str(e)) from e

    @abstractmethod
    def convert_to_pandas(self, dataframe):
        """To be overridden by child classes"""
        raise NotImplementedError("Subclass must implement convert_to_pandas")
    
    @abstractmethod
    def convert_to_spark(self, dataframe):
        """To be overridden by child classes"""
        raise NotImplementedError("Subclass must implement convert_to_spark")


# CHILD CLASSES - ENGINE SPECIFIC IMPLEMENTATIONS

class SparkReadOrWriteFiles(ReadOrWriteFiles):
    """Spark engine implementation - supports both pandas and spark"""
    
    def read_csv(self, engine, file_name, **kwargs):
        try:
            file_path = self.create_file_path(file_name)
            if engine == "pandas":
                dataframe = pd.read_csv(file_path, **kwargs)
                return dataframe
            elif engine == "spark":
                from pyspark.sql import SparkSession
                ReadSpark = SparkSession.builder.appName("ReadSpark").getOrCreate()
                dataframe = ReadSpark.read.options(**kwargs).csv(f"file:///{file_path}")
                return dataframe
            else:
                raise Exception(f"Unsupported engine: {engine}")
        except ImportError as e:
            raise Exception(f"Required engine '{engine}' is not available: {str(e)}") from e
        except Exception as e:
            raise Exception(str(e)) from e
        
    def read_excel(self, engine, file_name, **kwargs):
        try:
            file_path = self.create_file_path(file_name)
            if engine == "pandas":
                dataframe = pd.read_excel(file_path, **kwargs)
                return dataframe
            elif engine == "spark":
                from pyspark.sql import SparkSession
                ReadSpark = SparkSession.builder.appName("ReadSpark").config("spark.jars.packages", "com.crealytics:spark-excel_2.12:3.3.3_0.20.3").getOrCreate()
                config = {'header': True}
                config.update(kwargs)
                reader = ReadSpark.read.format("com.crealytics.spark.excel")
                for key, value in config.items():
                    reader = reader.option(key, value)
                dataframe = reader.load(f"file:///{file_path}")
                return dataframe
            else:
                raise Exception(f"Unsupported engine: {engine}")
        except ImportError as e:
            raise Exception(f"Required engine '{engine}' is not available: {str(e)}") from e
        except Exception as e:
            raise Exception(str(e)) from e
        
    def write_csv(self, engine, file_name, dataframe, **kwargs):
        try:
            file_path = self.create_file_path(file_name)
            if engine == "pandas":
                if isinstance(dataframe, pd.DataFrame):
                    dataframe.to_csv(file_path, index=False, **kwargs)
                    return True  
                else:
                    raise Exception(f"The provided DataFrame is not a pandas DataFrame. Please provide a pandas DataFrame.")
            elif engine == "spark":
                from pyspark.sql import SparkSession
                import pyspark.sql.dataframe
                if isinstance(dataframe, pyspark.sql.dataframe.DataFrame):
                    mode = kwargs.get("mode", "overwrite")
                    dataframe.repartition(1).write.mode(mode).options(**kwargs).csv(f"file:///{file_path}")
                    return True     
                else:
                    raise Exception(f"The provided DataFrame is not a Spark DataFrame. Please provide a Spark DataFrame.")  
            else:
                raise Exception(f"Unsupported engine: {engine}")
        except ImportError as e:
            raise Exception(f"Required engine '{engine}' is not available: {str(e)}") from e
        except Exception as e:
            raise Exception(str(e)) from e
        
    def write_excel(self, engine, file_name, dataframe, **kwargs):
        try:
            file_path = self.create_file_path(file_name)
            if engine == "pandas":
                if isinstance(dataframe, pd.DataFrame):
                    dataframe.to_excel(file_path, index=False, engine='openpyxl', **kwargs)
                    return True 
                else:
                    raise Exception(f"The provided DataFrame is not a pandas DataFrame. Please provide a pandas DataFrame.") 
            elif engine == "spark":
                from pyspark.sql import SparkSession
                import pyspark.sql.dataframe
                if isinstance(dataframe, pyspark.sql.dataframe.DataFrame):
                    mode = kwargs.get("mode", "overwrite")
                    config = {'header': True}
                    config.update(kwargs)
                    dataframe.repartition(1).write.format("com.crealytics.spark.excel").options(**config).mode(mode).save(f"file:///{file_path}")
                    return True
                else:
                    raise Exception(f"The provided DataFrame is not a Spark DataFrame. Please provide a Spark DataFrame.")       
            else:
                raise Exception(f"Unsupported engine: {engine}")
        except ImportError as e:
            raise Exception(f"Required engine '{engine}' is not available: {str(e)}") from e
        except Exception as e:
            raise Exception(str(e)) from e


class DltReadOrWriteFiles(ReadOrWriteFiles):
    """DLT engine implementation - pandas only"""
    
    def read_csv(self, engine, file_name, **kwargs):
        try:
            file_path = self.create_file_path(file_name)
            if engine == "pandas":
                dataframe = pd.read_csv(file_path, **kwargs)
                return dataframe
            elif engine == "spark":
                raise Exception("Spark engine is not supported in DLT mode. Use engine='pandas'")
            else:
                raise Exception(f"Unsupported engine: {engine}")
        except Exception as e:
            raise Exception(str(e)) from e
        
    def read_excel(self, engine, file_name, **kwargs):
        try:
            file_path = self.create_file_path(file_name)
            if engine == "pandas":
                dataframe = pd.read_excel(file_path, **kwargs)
                return dataframe
            elif engine == "spark":
                raise Exception("Spark engine is not supported in DLT mode. Use engine='pandas'")
            else:
                raise Exception(f"Unsupported engine: {engine}")
        except Exception as e:
            raise Exception(str(e)) from e
        
    def write_csv(self, engine, file_name, dataframe, **kwargs):
        try:
            file_path = self.create_file_path(file_name)
            if engine == "pandas":
                if isinstance(dataframe, pd.DataFrame):
                    dataframe.to_csv(file_path, index=False, **kwargs)
                    return True  
                else:
                    raise Exception(f"The provided DataFrame is not a pandas DataFrame. Please provide a pandas DataFrame.")
            elif engine == "spark":
                raise Exception("Spark engine is not supported in DLT mode. Use engine='pandas'")
            else:
                raise Exception(f"Unsupported engine: {engine}")
        except Exception as e:
            raise Exception(str(e)) from e
        
    def write_excel(self, engine, file_name, dataframe, **kwargs):
        try:
            file_path = self.create_file_path(file_name)
            if engine == "pandas":
                if isinstance(dataframe, pd.DataFrame):
                    dataframe.to_excel(file_path, index=False, engine='openpyxl', **kwargs)
                    return True 
                else:
                    raise Exception(f"The provided DataFrame is not a pandas DataFrame. Please provide a pandas DataFrame.") 
            elif engine == "spark":
                raise Exception("Spark engine is not supported in DLT mode. Use engine='pandas'")
            else:
                raise Exception(f"Unsupported engine: {engine}")
        except Exception as e:
            raise Exception(str(e)) from e


class SparkDataframeInformation(DataframeInformation):
    """Spark engine implementation - supports both pandas and spark DataFrames"""
    
    def convert_to_pandas(self, dataframe):
        try:
            try:
                import pyspark.sql.dataframe
                if isinstance(dataframe, pyspark.sql.dataframe.DataFrame):
                    return dataframe.toPandas()
            except ImportError:
                pass  # PySpark not available, continue with pandas check
            
            if isinstance(dataframe, pd.DataFrame):
                return dataframe  # Already a Pandas DataFrame
            else:
                raise Exception("Unsupported DataFrame type. Must be either Spark DataFrame or Pandas DataFrame.")
        except Exception as e:
            raise Exception(str(e)) from e
    
    def convert_to_spark(self, dataframe):
        try:
            # Import PySpark
            from pyspark.sql import SparkSession
            import pyspark.sql.dataframe
            
            PandasToSpark = SparkSession.builder.appName("PandasToSpark").getOrCreate()
            if isinstance(dataframe, pyspark.sql.dataframe.DataFrame):
                return dataframe
            elif isinstance(dataframe, pd.DataFrame):
                sparkDataframe = PandasToSpark.createDataFrame(dataframe)
                return sparkDataframe
            else:
                raise Exception("Unsupported DataFrame type. Must be either Spark DataFrame or Pandas DataFrame.")
        except ImportError as e:
            raise Exception(f"PySpark is not available: {str(e)}") from e
        except Exception as e:
            raise Exception(str(e)) from e


class DltDataframeInformation(DataframeInformation):
    """DLT engine implementation - pandas only"""
    
    def convert_to_pandas(self, dataframe):
        try:
            if isinstance(dataframe, pd.DataFrame):
                return dataframe  # Already a Pandas DataFrame
            else:
                raise Exception("Unsupported DataFrame type. Must be a Pandas DataFrame.")
        except Exception as e:
            raise Exception(str(e)) from e
    
    def convert_to_spark(self, dataframe):
        raise Exception("Spark conversion is not supported in DLT mode. Use Spark engine instead.")

# FACTORY FUNCTIONS

def create_file_operations(engine_type, user_id, basepath):
    """Factory function to create file operations based on engine type"""
    if engine_type == "dlt":
        return DltReadOrWriteFiles(user_id, basepath)
    elif engine_type == "spark":
        return SparkReadOrWriteFiles(user_id, basepath)
    else:
        raise ValueError(f"Unsupported engine type: {engine_type}. Must be 'dlt' or 'spark'")


def create_dataframe_operations(engine_type, config_dict={}):
    """Factory function to create dataframe operations based on engine type"""
    if engine_type == "dlt":
        return DltDataframeInformation(config_dict)
    elif engine_type == "spark":
        return SparkDataframeInformation(config_dict)
    else:
        raise ValueError(f"Unsupported engine type: {engine_type}. Must be 'dlt' or 'spark'")