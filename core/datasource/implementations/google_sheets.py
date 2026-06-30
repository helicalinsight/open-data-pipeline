"""
Core Google Sheets data-source connector.

Handles connections to Google Sheets via the gspread library and
Google service-account credentials.
"""

import logging
from typing import Any, Dict, List, Optional

from core.datasource.base import DBConnection
from core.datasource.exceptions import DataSourceException
from core.datasource.utils import map_columns

logger = logging.getLogger(__name__)


class GoogleSheets(DBConnection):
    """
    Google Sheets connector using ``gspread``.

    ``get_connection_string()`` and ``get_engine()`` raise
    ``NotImplementedError`` — Google Sheets is not an RDBMS.
    """

    def connect(self, connection_details: Dict[str, Any], engine: Optional[str] = None) -> Any:
        """Authorise and return a ``gspread.Client``."""
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials

        try:
            credentials_object = connection_details.get("credentials_object")
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                credentials_object.get("file"), scope
            )
            client = gspread.authorize(creds)
            logger.info("Connected to Google Sheets.")
            return client
        except Exception as e:
            logger.error("Failed to connect to Google Sheets: %s", e, exc_info=True)
            raise DataSourceException(
                f"Error while connecting to Google Sheets: {e}"
            ) from e

    def test_connection(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Test access to the Google Sheet."""
        if not connection:
            connection = self.connect(connection_details)
        try:
            sheet = connection.open_by_key(connection_details["sheet_id"])
            worksheet_titles = [ws.title for ws in sheet.worksheets()]
            if worksheet_titles and worksheet_titles[0]:
                logger.info("Google Sheets connection test passed.")
                return True
            return False
        except PermissionError as e:
            logger.error("Google Sheets permission error: %s", e, exc_info=True)
            raise DataSourceException(
                "Error while testing Google Sheets due to PermissionError. "
                "Make sure the Google Sheets API is enabled for your project."
            ) from e
        except Exception as e:
            logger.error("Google Sheets test failed: %s", e, exc_info=True)
            raise DataSourceException(
                f"Error while testing Google Sheets: {e}"
            ) from e

    def fetch_data(
        self,
        connection_details: Dict[str, Any],
        catalog: str,
        columns: Optional[List[str]] = None,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
        num_rows: int = 100,
    ) -> Any:
        """Fetch sheet data as a DataFrame."""
        import pandas as pd

        if columns is None:
            columns = []
        if not connection:
            connection = self.connect(connection_details)
        try:
            sheet = connection.open_by_key(connection_details["sheet_id"])
            sheet_instance = sheet.worksheet(catalog)
            records_data = sheet_instance.get_all_records()

            if columns:
                records_data = [{key: entry[key] for key in columns} for entry in records_data]
            if num_rows:
                records_data = records_data[:num_rows]

            dataframe = pd.DataFrame.from_dict(records_data)
            dataframe = dataframe.astype(
                {c: "str" for c in dataframe.select_dtypes(include=["object"]).columns}
            )
            dataframe.columns = map_columns(dataframe)
            logger.info("Fetched data from Google Sheets.")
            return dataframe
        except Exception as e:
            logger.error("Failed to fetch Google Sheets data: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to fetch the data: {e}") from e

    def get_metadata(
        self,
        connection_details: Dict[str, Any],
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Retrieve worksheet names from the spreadsheet."""
        if not connection:
            connection = self.connect(connection_details)
        try:
            data_catalog: List[Dict[str, Any]] = []
            sheet = connection.open_by_key(connection_details["sheet_id"])
            sheet_entry = {"title": sheet.title, "value": sheet.title, "children": []}
            for work_sheet in sheet:
                sheet_entry["children"].append(
                    {"title": work_sheet.title, "value": work_sheet.title, "children": []}
                )
            data_catalog.append(sheet_entry)
            logger.info("Fetched Google Sheets metadata.")
            return data_catalog
        except Exception as e:
            logger.error("Failed to get Google Sheets metadata: %s", e, exc_info=True)
            raise DataSourceException(f"Failed to get metadata: {e}") from e

    def get_columns(
        self,
        connection_details: Dict[str, Any],
        work_sheet_name: str,
        engine: Optional[str] = None,
        connection: Optional[Any] = None,
    ) -> Any:
        """Retrieve column names from a worksheet."""
        if not connection:
            connection = self.connect(connection_details)
        try:
            sheet = connection.open_by_key(connection_details["sheet_id"])
            sheet_instance = sheet.worksheet(work_sheet_name)
            records_data = sheet_instance.get_all_records()
            columns = list(records_data[0].keys())
            logger.info("Fetched columns for sheet %s.", work_sheet_name)
            return columns
        except Exception as e:
            logger.error(
                "Failed to get columns for sheet %s: %s", work_sheet_name, e, exc_info=True
            )
            raise DataSourceException(
                f"Failed to get columns for sheet {work_sheet_name}: {e}"
            ) from e
