class ManagerException(Exception):
    pass

class DataTransformationException(Exception):
    pass

class MetadataException(Exception):
    pass

class ExecuteException(Exception):
    pass
from core.exceptions import MongoException

class UtilsException(Exception):
    pass

class PreviewException(Exception):
    pass

from core.datasource.exceptions import DataSourceException as DatabaseConnectorException

class PyToolException(Exception):
    pass

class RateLimitException(Exception):
    pass


class LangchainServiceException(Exception):
    def __init__(self, error_response, status_code):
        self.error_response = error_response
        self.status_code = status_code
        super().__init__(error_response.get('msg', 'Task processing failed '))