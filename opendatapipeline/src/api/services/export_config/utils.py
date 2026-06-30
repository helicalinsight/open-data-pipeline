import ast
from ....exceptions.exceptions import UtilityException
from ....logger.logger import Logger, logger
class ExportUtils:
	"""Utility class for generating parameters and converting data types.

    Provides methods for generating parameters based on input details and converting
    string representations of data back to their original types.
    """
	@Logger.generate
	def generate_parameters(self,details):
		"""Generates parameters based on the provided details.

        This method generates a list of parameter dictionaries based on the input
        details. It specifically handles cases where the type is 'database' and
        there is a list of files. It creates a catalog dictionary mapping file IDs
        to catalog entries.

        :param details: A dictionary containing input details, including 'files_list',
                        'type', 'database', 'connection_id', and 'catalog'.
        :type details: dict
        :return: A tuple where the first element is a boolean indicating success, and
                 the second element is a list of dictionaries containing the generated
                 parameters.
        :rtype: tuple (bool, list)
        :raises UtilityException: If there is an issue generating the parameters.
        """
		parameters = []
		try:
			"""
			Generate parameters based on the provided details.

			Parameters:
			- details (dict): Input details containing files_list, type, database, connection_id, and catalog.

			Returns:
			- parameters (list): List of dictionaries containing parameters.
			"""

			if details.get("type") == "database" and details.get("files_list"):
				file_list = details["files_list"]
				connection_id = details.get("connection_id")
				catalog = details.get("catalog")

				if len(file_list) == 1 and catalog:
					file_id = file_list[0]["file_id"]

					if isinstance(catalog, list):
						catalog_dict = {file_id: cat for cat in catalog}
					else:
						catalog_dict = {file_id: catalog}

					parameter = {
						"database": {
							"catalog": catalog_dict
						}
					}

					parameters.append(parameter)
			logger.info("Successfully generated parameters")
			return True, parameters
		except Exception as e: # pragma: no cover
			logger.error("Unable to generate parameters", exc_info=True)
			raise UtilityException("Unable to generate parameters") from e
			# return False, parameters
   
	@Logger.generate
	def convert_string_to_original_type(self,input_string):
		"""Converts a string representation of a data type to its original type.

        This method attempts to evaluate the input string as a Python literal. If the
        evaluation fails, it returns the input string as is.

        :param input_string: The string representation of the data to be converted.
        :type input_string: str
        :return: The original data type if the evaluation succeeds, otherwise the input
                 string.
        :rtype: Any
        """
		# Handle the case when json data structure is passed instead of strigified version
		if not isinstance(input_string, str):
			return input_string
		try:
			# Attempt to evaluate the input string as a Python literal
			result = ast.literal_eval(input_string)
		except (ValueError, SyntaxError, TypeError):
			# If evaluation fails, return the input string as is
			result = input_string
		return result

	@Logger.generate
	def convert_dict_strings_to_original_types(self,input_dict):
		"""Converts all string values in a dictionary to their original types.

        This method iterates over the dictionary and converts each string value to its
        original type using the `convert_string_to_original_type` method.

        :param input_dict: A dictionary where the values are string representations of
                           data types.
        :type input_dict: dict
        :return: A new dictionary with string values converted to their original types.
        :rtype: dict
        """
		converted_dict = {}
		for key, value in input_dict.items():
			converted_dict[key] = self.convert_string_to_original_type(value)
		return converted_dict