
import yaml
from ....exceptions.exceptions import UtilityException
from ....logger.logger import Logger, logger
class ReadFile:
    """
    Class to handle reading of YAML files.
    """
    @Logger.generate
    def yml_reader(self, yml_path):
        """
        Reads a YAML file and returns its contents.

        :param yml_path: Path to the YAML file.
        :type yml_path: str
        :return: The contents of the YAML file.
        :rtype: dict
        :raises UtilityException: If the YAML file cannot be read.
        """
        try:
            with open(yml_path, "r") as config_file:
                config = yaml.safe_load(config_file)
                logger.info("Successfully performed yml reader")
                return config
        except Exception as e: # pragma: no cover
            logger.error("Unable to perform yml reader", exc_info=True)
            raise UtilityException("Unable to perform yml reader") from e
            # return None
