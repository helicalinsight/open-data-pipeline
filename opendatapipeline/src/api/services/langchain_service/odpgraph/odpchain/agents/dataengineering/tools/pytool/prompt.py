from ..........logger.logger import logger, Logger
import json
 
def get_pytool_prompt(dfs, df_names, task_description):
    schema_text = ""
    sample_data_json = ""

    for name, df in dfs.items():
        schema_lines = [f"- {col} ({name}): {dtype}" for col, dtype in df.dtypes.items()]
        schema_text += f"\nDataFrame '{name}':\n" + "\n".join(schema_lines)

        samples = df.head(3).to_dict(orient="records")
        sample_data_json += f"\nDataFrame '{name}':\n" + json.dumps(samples, indent=2, default=str)

    aliases = ", ".join(f'"{name}"' for name in df_names)
    logger.info(f"in get_pytool_prompt")
    PYTOOL_PROMPT = f"""
    You are a Python Pandas coding assistant. Your task is to generate Python code using the pandas library only.

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
    - Perform your operations.
    - Use `DataframeInformation.update` to store it back. NEVER call `.update()` directly on the DataFrame variable (e.g., `df.update(...)` is strictly forbidden).
    - Use `DataframeInformation.create` to create a new dataframe.
    - Both `pandas` (as `pd`) and the `DataframeInformation` utility are already injected into your global execution scope. DO NOT write import statements for them.
    - Do not assume anything. Analyze the complete sample data and schema based on the task.
    - Only return the code. No explanation.
    """
    return PYTOOL_PROMPT
