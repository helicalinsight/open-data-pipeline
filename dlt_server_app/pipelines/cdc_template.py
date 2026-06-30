"""
Sample CDC Pipeline Template for DLT
This is a basic template that can be customized for different sources
"""

import dlt
from dlt.sources.helpers import requests
from typing import Iterator, Dict, Any
import logging

logger = logging.getLogger(__name__)

@dlt.resource(name="incremental_table", write_disposition="merge")
def incremental_source(
    connection_string: str,
    table_name: str,
    cursor_column: str = "updated_at",
    primary_key: str = "id"
) -> Iterator[Dict[str, Any]]:
    """
    Basic incremental source for CDC
    
    Args:
        connection_string: Database connection string
        table_name: Name of the table to sync
        cursor_column: Column to use for incremental loading
        primary_key: Primary key column
    """
    
    # This is a template - actual implementation would vary by source
    logger.info(f"Starting incremental sync for table: {table_name}")
    
    # Placeholder for actual data fetching logic
    # In real implementation, this would:
    # 1. Connect to source database
    # 2. Get last cursor value from DLT state
    # 3. Fetch new/updated records
    # 4. Yield data with proper deduplication
    
    sample_data = [
        {primary_key: 1, "name": "Sample Record", cursor_column: "2024-01-01T00:00:00Z"},
        {primary_key: 2, "name": "Another Record", cursor_column: "2024-01-02T00:00:00Z"}
    ]
    
    for record in sample_data:
        yield record

def create_cdc_pipeline(source_config: Dict[str, Any], dest_config: Dict[str, Any]) -> dlt.Pipeline:
    """
    Create a CDC pipeline with the given configuration
    
    Args:
        source_config: Source database configuration
        dest_config: Destination configuration
        
    Returns:
        Configured DLT pipeline
    """
    
    pipeline_name = f"cdc_pipeline_{dest_config.get('dataset_name', 'default')}"
    
    pipeline = dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=dest_config.get('type', 'postgres'),
        dataset_name=dest_config.get('dataset_name', 'cdc_data'),
        progress="log"
    )
    
    return pipeline
