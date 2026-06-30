"""
Core datasource exceptions.
"""


class DataSourceException(Exception):
    """
    Exception raised for errors in datasource connector operations.

    This is a drop-in replacement for the legacy
    ``DatabaseConnectorException`` from ``opendatapipeline``.
    """
    pass
