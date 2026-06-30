from .utils import ReadFile

from ....configurations.api.config import  SourceConfig
from ....exceptions.exceptions import UtilityException
from ....logger.logger import Logger, logger



class DatasourcesService:
    """
    Service class for fetching datasources configuration.
    """
    def __init__(self, session=None) -> None:
        """
        Initialize the service with a session.

        :param session: The session object to use.
        :type session: Session
        """
        self.session = session
        
    @Logger.generate
    def get_datasources(self):
        """
        Fetches datasources configuration from a YAML file.

        :return: A tuple containing the status and the response dictionary.
        :rtype: tuple
        """
        try:
            read_file = ReadFile()
            config = read_file.yml_reader(SourceConfig.yml_path)

            if config:
                logger.info("Datasources fetched successfully.")
                return {
                    "success": True,
                    "configuration": config,
                    "msg": "Datasources fetched successfully."
                }, 200
            else: # pragma: no cover
                logger.error("No datasources found.", exc_info=True)
                raise Exception(f"No datasources found with config: {config}")
            
        except UtilityException as e: # pragma: no cover
            logger.error(f"{e}", exc_info=True)
            return {
                "success": False,
                "configuration": None,
                "msg": f"{e}"
                # "msg": "Error fetching datasources."
            }, 500

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {
                "success": False,
                "configuration": None,
                "msg": f"{e}"
                # "msg": "Error fetching datasources."
            }, 500

