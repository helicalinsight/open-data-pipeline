
import yaml
from ....exceptions.exceptions import UtilityException
from ....logger.logger import Logger, logger
class ReadFile:
    """Utility class for reading files and YAML configurations.

    Provides methods for reading YAML configuration files and other text files.
    The class handles file reading and parses YAML data as needed.
    """
    @Logger.generate
    def yml_reader(self, yml_path):
        """Reads and parses a YAML file.

        Opens the specified YAML file, parses its content, and returns the
        configuration data as a dictionary.

        :param yml_path: The path to the YAML file to be read.
        :type yml_path: str
        :return: The parsed YAML configuration data.
        :rtype: dict
        :raises UtilityException: If there is an error reading or parsing the YAML file.
        """
        try:
            with open(yml_path, "r") as config_file:
                config = yaml.safe_load(config_file)
                logger.info("Successfully performed yml reader")
                return config
        except Exception as e: # pragma: no cover
            logger.error("Unable to perform yml reader", exc_info=True)
            raise UtilityException("Unable to perform yml reader") from e
        
    @Logger.generate
    def file_reader(self, path):
        """Reads the content of a text file.

        Opens the specified file and returns its content as a string.

        :param path: The path to the text file to be read.
        :type path: str
        :return: The content of the file as a string.
        :rtype: str
        :raises UtilityException: If there is an error reading the file.
        """
        try:
            with open(path, 'r') as config_file:
                config = config_file.read()
            logger.info("Successfully read the file")
            return config
        except Exception as e: # pragma: no cover
            logger.error(f"Unable to read file: {str(e)}", exc_info=True)
            raise UtilityException(f"Unable to read file: {str(e)}")  from e
        