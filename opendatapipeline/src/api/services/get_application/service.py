from .utils import ReadFile

from ....configurations.api.config import  *


from ....models.mongo.mongo_factory import MongoFactory
from ....configurations.api.config import BaseConfig
from ....exceptions.exceptions import UtilityException

from ....models.connector import MongoConnector
from ....logger.logger import Logger, logger
from ..base.service_parent import ServiceParent


class ApplicationService(ServiceParent):
    """Service class for managing application configurations and documentation.

    Provides methods for retrieving application configurations and related documentation
    based on user ID. The configurations and documentation are read from specified files
    and returned as part of the response.
    """
    def __init__(self, session=None):
        """Constructor method for initializing the ApplicationService.

        :param session: The database session object.
        :type session: Session
        """
        self.session = session
        super().__init__(session)
        
    @Logger.generate
    def get_appservice(self, user_id):
        """Fetches application configurations and documentation for the given user ID.

        Retrieves user data from MongoDB, reads configuration and documentation files,
        and returns them as part of the response. The method looks up the application
        configuration based on the user's role and provides documentation in YAML and
        Python formats.

        :param user_id: The ID of the user whose application configuration and documentation are to be fetched.
        :type user_id: str
        :return: A dictionary containing success status, application configuration,
                 job help information, and a message.
        :rtype: dict
        :raises Exception: If application settings or documentation are not found.
        """
        try:
            users = MongoFactory(self.client, "users", session=self.session)
            status, users_data=users.get_by_id(user_id)
            read_file = ReadFile()

            config = read_file.yml_reader(SourceConfig.application_path)
            python_documentation = read_file.file_reader(SourceConfig.python_md_file_path)
            yaml_documentation = read_file.file_reader(SourceConfig.yaml_md_file_path)
            job_arguments_documentation = read_file.file_reader(SourceConfig.job_args_help_path)
            schedule = read_file.yml_reader(SourceConfig.schedule_path)
            version = Config().config.get('build', 'version')
            documentation = {
                "yaml": yaml_documentation,
                "python": python_documentation,
                "job_arguments": job_arguments_documentation
            }
            if all([config, documentation, version]):
                application = config.get(users_data["role"],None)
                editor_configuration = config.get('editor_configurations')
                schedule_configuration = schedule.get('schedule')
                logger.info("Application Configurations and editor Configurations Fetched Successfully!")
                logger.warning("The 'connection' variable is deprecated. Use the 'Connection' class instead.")
                
                return {
                    "success": True,
                    "configuration": application,
                    "editor_configuration": editor_configuration,
                    "schedule_configuration": schedule_configuration,
                    "job_help_info": documentation,
                    "version": version,
                    "msg": "Application Configurations and editor Configurations Fetched Successfully!",
                    "deprecated" : "The 'connection' variable is deprecated. Use the 'Connection' class instead."
                }, 200
            else: # pragma: no cover
                logger.error("No Application settings or documentation found.", exc_info=True)
                raise Exception(f"No Application settings or documentation found with user_id: {user_id}")
            
        except UtilityException as e: # pragma: no cover
            logger.error("Error fetching Application.", exc_info=True)
            return {
                "success": False,
                "configuration": None,
                "job_help_info": None,
                "editor_configuration": None,
                "schedule_configuration": None,
                "version": None,
                "msg": "Error fetching Application."
            }, 500

        except Exception as e: # pragma: no cover
            logger.error(f"Operation Completed with Exception: {e}", exc_info=True)
            return {
                "success": False,
                "configuration": None,
                "job_help_info": None,
                "editor_configuration": None,
                "schedule_configuration": None,
                "version": None,
                "msg": "Error fetching Application."
            }, 500

