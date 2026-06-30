from ....exceptions.exceptions import UtilityException
from ....logger.logger import Logger, logger
class DataLoadsUtilities:
    """
    Utility class for processing data loads, including separating catalog details
    and processing file types.
    """
    @Logger.generate
    def separate_catalog_with_file_name(self,input_dict):
        """
        Separates catalog details with file names from the input dictionary.

        :param input_dict: The input dictionary containing catalog details and additional information.
        :type input_dict: dict
        :param input_dict['source']: The source from which the catalogs are being processed (e.g., file path or database name).
        :type input_dict['source']: str
        :param input_dict['details']: Details related to the catalogs and file processing.
        :type input_dict['details']: dict
        :param input_dict['details']['connection_id']: The ID of the database connection.
        :type input_dict['details']['connection_id']: str
        :param input_dict['details']['chat_id']: The ID of the chat associated with the operation.
        :type input_dict['details']['chat_id']: str
        :param input_dict['details']['file_name']: The name of the file to be processed.
        :type input_dict['details']['file_name']: str
        :param input_dict['details']['user_id']: The ID of the user initiating the operation.
        :type input_dict['details']['user_id']: str
        :param input_dict['details']['database_name']: The name of the database related to the catalogs.
        :type input_dict['details']['database_name']: str
        :param input_dict['details']['catalog']: A dictionary where keys are catalog names and values are column details.
        :type input_dict['details']['catalog']: dict
        :param input_dict['details']['source_id']: The ID of the source, optional.
        :type input_dict['details']['source_id']: str, optional
        :return: A tuple with a boolean status and the result list containing separated catalog details.
        :rtype: tuple
        :return:
            - status (bool): Indicates whether the separation was successful.
            - result_list (list of dict): A list of dictionaries with separated catalog details.
        :raises UtilityException: If there is an issue separating the catalog details.
        """
        result_list = []
        try:
            source = input_dict.get("source")
            details = input_dict.get("details", {})
            connection_id = details.get("connection_id")
            chat_id = details.get("chat_id")
            file_name = details.get("file_name")
            user_id = details.get("user_id")
            database_name=details.get("database_name")
            catalog_list = details.get("catalog", {})
            source_id = details.get("source_id",None)


            for catalog, columns in catalog_list.items():
                result_dict = {
                    "source": source,
                    "details": {
                        "connection_id": connection_id,
                        "chat_id": chat_id,
                        "type": "table",
                        "file_name": catalog,
                        "catalog": catalog,
                        "columns" : columns,
                        "user_id":user_id,
                        "database_name":database_name
                    }
                }
                if source_id:
                    result_dict["details"]["source_id"]=source_id
                result_list.append(result_dict)
            logger.info("Successfully seperated catalog with file name")
            return True, result_list
        except Exception as e:# pragma: no cover
            logger.error("Unable to separate catalog with file name", exc_info=True)
            raise UtilityException("Unable to separate catalog with file name") from e
            # return False, result_list
    @Logger.generate
    def process_type_for_files(self, input_dict):
        """
        Processes the file type from the input dictionary.

        :param input_dict: The input dictionary containing file details.
        :type input_dict: dict
        :param input_dict['details']: Details related to the file processing.
        :type input_dict['details']: dict
        :param input_dict['details']['type']: The type of the file (e.g., 'csv', 'json', 'xlsx').
        :type input_dict['details']['type']: str
        :return: A tuple with a boolean status and the updated input dictionary.
        :rtype: tuple
        :return:
            - status (bool): Indicates whether the file type was processed successfully.
            - updated_input_dict (dict): The updated input dictionary with the processed file type.
        :raises UtilityException: If there is an issue processing the file type.
        """
        try:
            details = input_dict.get("details", {})
            type=details.get("type")
            type=type.split(".")[-1]
            details["type"]=type
            details["file_id"]= details.get("connection_id")
            input_dict["details"]=details
            logger.info("Successfully prcessed type for files")
            return True, input_dict
        except Exception as e:# pragma: no cover
            logger.error("Unable to process type for files", exc_info=True)
            raise UtilityException("Unable to process type for files") from e
            # return False, input_dict

    def process_catalog_for_s3(self, input_dict, file_name, file_type, catalog):
        result_list = []
        if catalog is None:
            # for files with children as empty
            catalog = catalog or file_name
            input_dict["details"]["catalog"] = catalog
            result_list.append(input_dict)
        else:
            # for files with children
            for file_path, columns in catalog.items():
                result = {
                    "file_name": file_path,
                    "catalog": file_path,
                    "columns": columns
                }
            input_dict['details'].update(result)
            result_list.append(input_dict)
        return True, result_list
