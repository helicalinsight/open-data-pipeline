import traceback
from typing import Dict, List
from ....logger.logger import Logger, logger
from ....exceptions.exception import *
from .helper.helper import DataframeInformation
from ....api.data.chat import Chat
import pandas as pd
import numpy as np
import fuzzywuzzy
import random
from langchain_core.tools import Tool


class PyTool:
    """
    This class is designed for executing code and includes a method called execute for performing the code execution

    """
    
    def execute_pandas_code(self, code: str, df: pd.DataFrame, df_alias: str, df_info: dict) -> str:
        logger.info(f"in execute_pandas_code df", df)
        local_vars = {'pd': pd, 'np': np, 'random': random, 'df': df.copy(), 'DataframeInformation': df_info}
        try:
            exec(code, local_vars, local_vars)
        except Exception as e:
            return f"Execution Error: {e}"

        # Return any new DataFrame created
        result = ""
        updated_df = local_vars.get('df')
        if isinstance(updated_df, pd.DataFrame):
            if df_info.get(alias=df_alias) is not None:
                df_info.update(alias=df_alias, dataframe=updated_df)
                result += f"\nUpdated df ({df_alias}):\n{updated_df}\n"
            else:
                df_info.create(id=df_alias, alias=df_alias, dataframe=updated_df)
                result += f"\nCreated new df ({df_alias}):\n{updated_df}\n"
        else:
            return "No valid DataFrame `df` found after execution."

        return result or "No result DataFrame produced."

    def _get_changed_id_alias(self, old_ids, new_ids) -> List[Dict]:
        diff_ids = [{"source_id": item[0], "dataframe_alias": item[1]} for item in new_ids if item not in old_ids]
        return diff_ids

    @Logger.generate
    def execute(self, dataframe_config, parameters, user_info, session):
        """
        Executes the provided Python code and returns a boolean value indicating the success or failure of the execution 

        :param dataframe_config: A dictionary of dataframes associated with id's
        :type dataframe_config: dict
        :param parameters: A dictionary which will have a code to execute
        :type parameters: dict
        :return:  A boolean indicating success or failure, A success message
        :rtype: bool, str
        """
        try:
            logger.info(f"Executing pytool..")
            logger.info(f"dataframe_config: {dataframe_config}")
            logger.info(f"parameters: {parameters}")
            logger.info(f"user_info: {user_info}")
            logger.info(f"session: {session}")

            # Initialize DataframeInformation
            dfinfo = DataframeInformation(dataframe_config, user_info, session)
            old_id_alias = dfinfo.get_all_id_alias()

            # Prepare globals for execution
            # NOTE: Consider explicitly restricting __builtins__ in global_scope for security to prevent RCE from malicious code.
            global_scope = {
                'DataframeInformation': dfinfo,
                'pd': pd,
                'np': np,
                'random': random,
                'fuzzywuzzy': fuzzywuzzy
            }

            # Execute user code
            cleaned_code = parameters.get("code", "")
            try:
                exec(cleaned_code, global_scope)
            except SyntaxError as e:
                logger.error(f"SyntaxError in LLM generated code:\n{cleaned_code}\nError: {e}")
                raise PyToolException(f"Syntax error in generated code: {e}") from e

            # Identify new or updated DataFrames
            new_id_alias = dfinfo.get_all_id_alias()
            output = self._get_changed_id_alias(old_id_alias, new_id_alias)

            # Update chat if there's a new dataframe created
            if output:
                Chat(session=session).update(user_info.get("chat_id"), "cwf", output[-1])

            message = "Executed the code successfully."
            logger.info(f"Execution complete. Output changes: {output}")
            return True, message, output, dfinfo.config_dict

        except Exception as e:
            logger.error(f"Failed to execute the code: {str(e)}", exc_info=True)
            tb_str = traceback.format_exc()
            raise PyToolException(f"Failed to execute the code. {str(e)}\n{tb_str}")
            """
            cleaned_code = parameters.get("code", "")
            df = parameters.get("df", "")
            logger.info(f"df {type(df)}")
            df_alias = parameters["df_alias"]
            df_info = parameters["df_info"]
            logger.info(f"df_info {df_info.__dict__} {type(df_info)}")
            pandas_tool = Tool.from_function(
                name="execute_pandas_code",
                description="Executes Python Pandas code on DataFrame 'df' and returns dataframe.",
                func=lambda code: self.execute_pandas_code(cleaned_code, df, df_alias, df_info)
            )
            result = pandas_tool.invoke({"input": cleaned_code})
            logger.info(f"Execution result: {result}")
            message = "Executed the code successfully."
            logger.info(f"df_alias {df_alias}")
            logger.info(f"message {message}")
            logger.info(f"df_info.config_dict {df_info.config_dict}")
            return True, message, df_alias, df_info.config_dict
        except Exception as e:
            logger.error(f"Failed to execute the code: {str(e)}", exc_info=True)
            tb_str = traceback.format_exc()
            raise PyToolException(f"Failed to execute the code. {str(e)}\n{tb_str}")
"""