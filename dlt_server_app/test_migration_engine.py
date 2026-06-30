from dlt_server_app.migrations.migration_engine import MigrationEngine
m = MigrationEngine()
print(f'MigrationEngine created OK, has datasource: {hasattr(m, "datasource")}')
cs = m._build_connection_string({'db_type': 'postgresql', 'host': 'localhost', 'port': 5432, 'database': 'test', 'username': 'user', 'password': 'pass'})
assert 'postgresql' in cs, f'Unexpected: {cs}'
print(f'Connection string via MigrationEngine OK: {cs}')
