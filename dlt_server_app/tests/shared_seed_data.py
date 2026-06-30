# dlt_server_app/tests/shared_seed_data.py
"""
Shared seed data for dlt_server_app tests.
Contains sample data that will be inserted into MongoDB collections during tests.
"""

from bson import ObjectId

# Schedule data for testing DLT pipeline scheduling
schedule = [
    {
        "_id": ObjectId("65cb43f2007a5f38718b9abc"),  
        "user_id": "dlt_test_user",
        "chat_id": "dlt_test_chat",
        "schedule_name": "DLT code smoke (prints hi)",
        "code": 'print("hi")',   
        "configurations": {},
        "pipeline": [],
        "next": []
    },
    {
        "_id": ObjectId("68be942caeab8bac1c175a81"),
        "chat_id": "68be9410aeab8bac1c175a7f",
        "user_id": "68b6d4e69349b8c6ac31279e",
        "schedule_name": "DLT sample code",
        "engine_type": "dlt",  
        "schedule_interval": "once",
        "generated_cron_expression": None,
        "advanced_scheduling": {},
        "pipeline": [],
        "configurations": {},
        "code": 'print("Hello from DLT")',
        "replace_connections": {},
        "notification": {
            "active": False,
            "type": "email",
            "details": {"to": None, "subject": None, "body": None}
        },
        "export_files_list": [],
        "type": "localstorage",
        "execution_type": "code",
        "job_details": {"export_format": "csv", "type": "localstorage"},
        "export_format": None,
        "meta_schedule_version": 2
    },
    {
        "_id": ObjectId("68c7a3029c8dc167ac6254c5"),
        "chat_id": "68c283239c8dc167ac6254c0",
        "user_id": "68b6d4e69349b8c6ac31279e",
        "schedule_name": "Test",
        "engine_type": "dlt",
        "schedule_interval": "once",
        "generated_cron_expression": None,
        "advanced_scheduling": {},
        "pipeline": [],
        "configurations": {},
        "code": "print(\"helloooo\")",
        "replace_connections": {},
        "notification": {
            "active": False,
            "type": "email",
            "details": {
                "to": None,
                "subject": None,
                "body": None
            }
        },
        "export_files_list": [],
        "type": "localstorage",
        "execution_type": "code",
        "job_details": {
            "type": "localstorage"
        },
        "export_format": "csv",
        "meta_schedule_version": 2
    },
    {
        "_id": ObjectId("65cb43f2007a5f38718b9d6c"),
        "user_id": "dlt_test_user",
        "chat_id": "dlt_test_chat",
        "schedule_name": "DLT e2e write (e2e.duckdb)",
        "engine_type": "dlt",
        "execution_type": "code",
        "pipeline": [],
        "configurations": {},
        "replace_connections": {},
        "code": (
            "import dlt\n"
            "pipe = dlt.pipeline(\n"
            '    pipeline_name="e2e_pipeline",\n'
            '    destination=dlt.destinations.duckdb("/app/data/e2e.duckdb"),\n'
            '    dataset_name="e2e_ds",\n'
            '    pipelines_dir="/app/.dlt",\n'
            '    progress="log",\n'
            ")\n"
            "rows = [\n"
            '    {\"id\": 1, \"val\": \"a\"},\n'
            '    {\"id\": 2, \"val\": \"b\"},\n'
            '    {\"id\": 3, \"val\": \"c\"},\n'
            "]\n"
            'info = pipe.run(rows, table_name="entries", write_disposition="replace")\n'
            'print("DONE", info.loads_ids)\n'
        ),
        "notification": {"active": False, "type": "email", "details": {"to": None, "subject": None, "body": None}},
        "export_files_list": [],
        "type": "localstorage",
        "job_details": {"export_format": "csv", "type": "localstorage"},
        "meta_schedule_version": 2,
    },
    {
    "_id": ObjectId("65cb43f2007a5f38718b9d7f"), 
    "user_id": "dlt_test_user",
    "chat_id": "dlt_test_chat",
    "schedule_name": "DLT write people to DuckDB",
    "engine_type": "dlt",
    "execution_type": "code",
    "pipeline": [],
    "configurations": {},
    "replace_connections": {},
    "code": """import dlt

pipe = dlt.pipeline(
    pipeline_name="people_pipeline",
    destination=dlt.destinations.duckdb("/app/data/people.duckdb"),
    dataset_name="people_ds",
    pipelines_dir="/app/.dlt",
    progress="log",
)

rows = [
    {"id": 101, "name": "Grace Hopper"},
    {"id": 102, "name": "Linus Torvalds"},
    {"id": 103, "name": "Katherine Johnson"},
]
info = pipe.run(rows, table_name="people", write_disposition="replace")
print("INSERTED_ROWS", len(rows), "LOAD_IDS", info.loads_ids)
""",
    "notification": {
        "active": False,
        "type": "email",
        "details": {"to": None, "subject": None, "body": None},
    },
    "export_files_list": [],
    "type": "localstorage",
    "job_details": {"export_format": "csv", "type": "localstorage"},
    "meta_schedule_version": 2,
}
]

# File data for testing file operations
files = [
    {
        "_id": ObjectId("65cb43f2007a5f38718b9abd"),
        "user_id": "dlt_test_user",
        "filename": "test_data.csv",
        "file_path": "/tmp/test_data.csv",
        "file_size": 1024,
        "upload_timestamp": "2024-02-12T10:00:00Z",
        "file_type": "csv",
        "status": "uploaded"
    },
    {
        "_id": ObjectId("65cb43f2007a5f38718b9abe"),
        "user_id": "dlt_test_user",
        "filename": "sample.json",
        "file_path": "/tmp/sample.json",
        "file_size": 512,
        "upload_timestamp": "2024-02-12T11:00:00Z",
        "file_type": "json",
        "status": "processed"
    }
]

# User data for testing user operations
users = [
    {
        "_id": ObjectId("68b6d4e69349b8c6ac31279e"),
        "user_id": "dlt_test_user",
        "username": "dlt_tester",
        "email": "dlt_test@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "status": "active",
        "role": "user"
    },
    {
        "_id": ObjectId("68b6d4e69349b8c6ac31279f"),
        "user_id": "dlt_admin_user",
        "username": "dlt_admin",
        "email": "admin@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "status": "active",
        "role": "admin"
    }
]

# Connection data for testing database connections
connections = [
    {
        "_id": ObjectId("65cb43f2007a5f38718b9abf"),
        "user_id": "dlt_test_user",
        "connection_name": "test_postgres",
        "connection_type": "postgres",
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "username": "test_user",
        "created_at": "2024-02-12T10:00:00Z",
        "status": "active"
    },
    {
        "_id": ObjectId("65cb43f2007a5f38718b9ac0"),
        "user_id": "dlt_test_user",
        "connection_name": "test_duckdb",
        "connection_type": "duckdb",
        "file_path": "./test.duckdb",
        "created_at": "2024-02-12T10:00:00Z",
        "status": "active"
    }
]

# Cache data for testing caching functionality
cache = [
    {
        "_id": ObjectId("65cb43f2007a5f38718b9ac1"),
        "cache_key": "dlt_test_pipeline_state",
        "cache_value": {"last_run": "2024-02-12T10:00:00Z", "status": "completed"},
        "user_id": "dlt_test_user",
        "created_at": "2024-02-12T10:00:00Z",
        "expires_at": "2024-02-13T10:00:00Z"
    }
]

# Langchain data for testing AI/ML operations
langchain = [
    {
        "_id": ObjectId("65cb43f2007a5f38718b9ac2"),
        "user_id": "dlt_test_user",
        "conversation_id": "dlt_test_conversation",
        "message_type": "user",
        "content": "How do I create a dlt pipeline?",
        "timestamp": "2024-02-12T10:00:00Z"
    },
    {
        "_id": ObjectId("65cb43f2007a5f38718b9ac3"),
        "user_id": "dlt_test_user",
        "conversation_id": "dlt_test_conversation",
        "message_type": "assistant",
        "content": "To create a dlt pipeline, you can use the @dlt.resource decorator...",
        "timestamp": "2024-02-12T10:01:00Z"
    }
]