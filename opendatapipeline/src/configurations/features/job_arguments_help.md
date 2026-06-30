## Job Arguments

Job arguments are key-value pairs that configure how a job behaves during its execution. Each job can have multiple arguments to control things like file handling modes, data processing configurations, and more. 

With Job arguments, you can provide custom configuration for any of the step of pipeline you plan to run or give job level configuration.

### Example of pipeline step level config

Key:

Key should have the format `__{STEP_NAME}__{STEP_NUMBER}` where {STEP_NAME} is the name of step you want to target and {STEP_NUMBER} is the 0-indexed step number of pipeline. 

Suppose you want to provide config for "read_files" step at 0th index of your pipeline, then key will be `__read_files__0`

Value:

Value is the config you want to use. 

Suppose you want to provide config of read_files "mode" to be "FAILFAST", then your value will be {"mode": "FAILFAST"}

### Example of job level config

Key:

Name of the configuration. Suppose you want to provide list of packages for the job, then Key would be `--packages`

Value:

Value can be a string with list of versions in this case - "org.firebirdsql.jdbc:jaybird:5.0.4.java11"


For further reading on possible values of Job Arguments, refer - https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html	 

## Common Use-cases for Job Arguments
| Key                    | Value                           | Description                                                                 |
|----------------------- |---------------------------------|-----------------------------------------------------------------------------|
| `__read_files__0`      |{"mode": "DROPMALFORMED"}        |Job would drop malformed records while reading the file at step 0 in pipeline|
|                        |{"mode": "FAILFAST"}             |Job would stop reading as soon as it encounters malformed record while reading the file at step 0 in pipeline|
| `__read_tables__1`     |{"dbtable": "table_a"}           |Job loads only `table_a` from the database at step 1 in pipeline|
| `--packages`           |<groupId>:<artifactId>:<version> |Job packages to define external libraries or dependencies from Maven Central, provided as a comma-separated list|
