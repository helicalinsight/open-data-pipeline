from ..........logger.logger import Logger,logger
import json

def get_sparktool_prompt(dfs, df_names, task_description, pandas_code):
    # Build DataFrame schema summary (name + dtype)
    schema_text = ""
    sample_data_json = ""

    for name, df in dfs.items():
        schema_lines = [f"- {col} ({name}): {dtype}" for col, dtype in df.dtypes.items()]
        schema_text += f"\nDataFrame '{name}':\n" + "\n".join(schema_lines)

        samples = df.head(1).to_dict(orient="records")
        sample_data_json += f"\nDataFrame '{name}':\n" + json.dumps(samples, indent=2, default=str)

    aliases = ", ".join(f'"{name}"' for name in df_names)
    logger.info(f"in get_sparktool_prompt")
    # Prompt to generate PySpark code
    SPARKTOOL_PROMPT = f"""
    You are a PySpark coding assistant. Your task is to generate PySpark code based on the task provided using the Pandas code provided and the `pyspark.sql` library only. 
    Below is the Pandas code for preserving the same column names, alias names, and logic.
    
```python
{pandas_code}

    You have access to a utility called `DataframeInformation`, which provides these methods:

    - `DataframeInformation.get(alias="<alias>")`: Use get to retrieve the existing dataframe by alias.
    - `DataframeInformation.update(alias="<alias>", dataframe=df)`: Use update when the dataframe already exists.
    - `DataframeInformation.create(id="<alias>", alias="<alias>", dataframe=df)`: Use create when the dataframe does not exist yet.

    Do not use a raw DataFrame variable like `df`. Instead, retrieve it from `DataframeInformation` using its alias, modify it, and update it back.

    Fetch DataFrames using aliases: {aliases}

    Schema:
    {schema_text}
    
    Sample Data:
    {sample_data_json}
    
    Task:
    {task_description}

    Instructions:
    - Use `DataframeInformation.get` to fetch the DataFrame using the utility provided.
    - Perform your transformations using PySpark SQL.
    - Use `DataframeInformation.update` to store it back.
    - Use `DataframeInformation.create` to create a new dataframe.
    - Import necessary libraries and functions for the code to execute.
    - Use only functions from `pyspark.sql.functions` that are officially supported.
    
    Date/Time Handling:
    - If the task requires any date or time operations, use only PySpark functions such as:
    `current_date()`, `current_timestamp()`, `to_date()`, `to_timestamp()`, `datediff()`, etc.
    - NEVER use `datetime`, `pandas`, `time`, or similar Python-based date/time libraries.
    - When using `datediff(a, b)`, it computes `a - b` in terms of days.

    Strict rules (follow exactly):
    - Do NOT use pandas libraries or pd. Instead use only PySpark related libraries.
    - Do NOT import functions that do not exist in PySpark.
    - NEVER use or mention or import `SparkSession`.
    - NEVER write comments or explanations.
    - NEVER refer to any object named `spark`, `SparkContext`, or similar.
    - When using `regexp_replace`, escape `$` in the replacement string by writing `"\\$"` and  `\` in the replacement string by writing `"\\\\"` to avoid `Illegal group reference` errors.
    - Use `withColumnRenamed(old_name, new_name)` with positional arguments only. Do NOT use keyword arguments like `colName=` or `newColName=`.
    - Simulate randomness by using `pyspark.sql.functions.rand()` combined with chained `.when()` conditions to assign values based on random thresholds.
    - Only return the code. No explanation.

    Prohibited:
    - Do NOT include `from pyspark.sql import ...`
    - Do NOT create or use `SparkSession.builder...`
    - Do NOT use Python's // operator for floor division on columns.
    """
    return SPARKTOOL_PROMPT
