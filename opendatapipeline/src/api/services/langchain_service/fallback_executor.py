import json
from .odpgraph.odpchain.agents.dataengineering.tools.pytool.main import PyToolAgent
from .odpgraph.odpchain.agents.dataengineering.tools.pytool.prompt import get_pytool_prompt
from .odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
import re
from .odpgraph.odpchain.agents.dataengineering.tools.sparktool.prompt import get_sparktool_prompt
from ....utilities.utilities import CommonUtils
from .odpgraph.odpchain.agents.dataengineering.tools.utils import extract_code
from ....logger.logger import logger, Logger
from ....api.services.pyspark_service.llm_chatbot import LLMChatBot
from typing import TypedDict, Any, Dict
import pandas as pd
from .odpgraph.odpchain.agents.context.context import Context
from .odpgraph.odpchain.agents.memory.memory import Memory
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
from ....configurations.api.config import Config
from langgraph.graph import StateGraph, END
from inbuilt_modules.helper.helper.helper import SparkDataframeInformation

class AgentState(TypedDict):
    dataframes: Dict[str, pd.DataFrame]
    selected_dataframes: pd.DataFrame
    selected_dataframe_names: str
    task_description: str
    generated_pandas_code: str
    generated_pyspark_code: str
    cleaned_pandas_code: str
    cleaned_pyspark_code: str


class FallBackExecutor:
        def __init__(self, user_id, chat_id, session, agent, spkagent):
                try:
                        logger.info("init")
                        self.session=session
                        self.user_id=user_id
                        self.chat_id= chat_id
                        self.agent = agent
                        self.spkagent = spkagent
                        
                        self.context = Context(self.session)
                        self.df_info = SparkDataframeInformation()
                except Exception as e:
                        logger.error(f"Error initializing FallBackExecutor: {str(e)}", exc_info=True)
                        raise Exception(f"Error initializing FallBackExecutor: {str(e)}") from e
                        
        def start_router(self, state: AgentState):
                return state

        def get_dataframes_node(self, state: AgentState) -> AgentState:
                df_dict = Context(self.session).get_dataframes(self.chat_id)
                logger.info(f"df_dict {df_dict}")
                state["dataframes"] = df_dict
                for alias, df in state["dataframes"].items():
                        self.df_info.create(alias=alias, id=alias, dataframe=df)
                logger.info(f"Loaded dataframes: {list(df_dict.keys())}")
                return state
        
        def make_json_serializable(self, obj):
                if isinstance(obj, dict):
                        return {k: self.make_json_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                        return [self.make_json_serializable(elem) for elem in obj]
                elif isinstance(obj, pd.Timestamp):
                        return str(obj)
                else:
                        return obj
        
        def get_dataframe_metadata(self, df: pd.DataFrame) -> dict:
                metadata = {
                        "columns": list(df.columns),
                        "dtypes": df.dtypes.astype(str).to_dict(),
                        "null_counts": df.isnull().sum().to_dict(),
                        "n_rows": df.shape[0],
                        "n_columns": df.shape[1],
                        "memory_usage_MB": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
                        "sample_rows": df.head(3).to_dict(orient="records"),
                        "summary_statistics": df.describe(include='all').to_dict()
                }
                return metadata
        
        # 2. Select DataFrame based on task
        def select_dataframe_node(self, state: AgentState) -> AgentState:
                task = state.get("task_description", "")
                logger.info(f"task {task}")
                dataframes = state["dataframes"]
                # Prepare dataframe schemas
                df_summaries = [
                        {
                                "name": name,
                                **self.get_dataframe_metadata(df)
                        }
                        for name, df in dataframes.items()
                ]

                df_summaries = self.make_json_serializable(df_summaries)
                valid_names = list(dataframes.keys())
                logger.info(f"valid_names {valid_names}")
                prompt = f"""
        You are given summaries of different dataframes:

        {json.dumps(df_summaries, indent=2, default=str)}

        A user has the following task:
        "{task}"

        Valid dataframe names: {valid_names}

        **Identify which dataframe(s) this task should be applied to.**
        Focus only on dataframes explicitly mentioned in the task, or those needed to fulfill it.
        Only reply with a valid JSON array of dataframe names (e.g., ["df1", "df2"]).
        Do NOT use markdown or ```json.
        """

                # Call LLM
                response = self.agent.invoke(prompt)
                logger.info(f"response {response}")
                # Extract JSON safely from markdown-wrapped or raw
                raw_response = response.content.strip()
                if "```python" in raw_response:
                        match = re.search(r"```python\s*(.*?)\s*```", raw_response, re.DOTALL)
                        cleaned_response = match.group(1) if match else raw_response.strip()
                else:
                        cleaned_response = raw_response.strip()

                logger.info(f"cleaned_response {cleaned_response}")
                try:
                        parsed = json.loads(cleaned_response)
                        selected_names = parsed if isinstance(parsed, list) else parsed.get("selected_dataframes", [])
                except json.JSONDecodeError as e:
                        raise ValueError(f"Could not parse LLM response:\n{raw_response}") from e
                logger.info(f"selected_names {selected_names}")

                # Create a lowercase mapping from dataframe name to actual name
                dataframe_name_map = {name.lower(): name for name in dataframes.keys()}
                # Normalize selected_names to lowercase
                selected_names_lower = [name.lower() for name in selected_names]

                # Normalize selected names and get matching dataframes
                selected_dataframes = {
                        dataframe_name_map[name]: dataframes[dataframe_name_map[name]]
                        for name in selected_names_lower
                        if name in dataframe_name_map
                }
                logger.info(f"selected_dataframes {selected_dataframes}")
                if not selected_dataframes:
                        raise ValueError("No valid dataframes selected by the LLM.")
                # Update state
                state["selected_dataframe_names"] = selected_names
                state["selected_dataframes"] = selected_dataframes
                return state

        # 3. Generate Pandas Code
        def pandas_code_generator_node(self, state: AgentState) -> AgentState:
                # Dummy code generation based on task
                task_description = state.get("task_description", "")
                dfs = state.get("selected_dataframes", "")
                df_names = state.get("selected_dataframe_names", "")
                logger.info(f"df_names {df_names}")
                pandas_query = get_pytool_prompt(dfs, df_names, task_description)
                # Generate code using LLM
                logger.info("Generating Pandas Code...")
                response = self.agent.invoke(pandas_query)
                generated_pandas_code = response.content.strip()
                state["generated_pandas_code"] = generated_pandas_code
                logger.info(f"Generated code: {generated_pandas_code}")
                return state

        def pandas_code_cleaner_node(self, state: AgentState) -> AgentState:
                # Remove ```python or ``` blocks
                logger.info("in pandas_code_cleaner")
                text = state.get("cleaned_pandas_code", "")
                code = re.sub(r"```(python)?", "", text)
                code = re.sub(r"```", "", code)
                # Remove comments or unnecessary explanations if needed (optional)
                lines = code.strip().split("\n")
                code_lines = []
                for line in lines:
                        cleaned_line = line.strip()
                        if cleaned_line.startswith("#"):
                                continue
                        # Filter out hallucinated imports
                        if "import " in cleaned_line and ("DataframeInformation" in cleaned_line or "pandas" in cleaned_line):
                                continue
                        code_lines.append(line)
                state["cleaned_pandas_code"] = "\n".join(code_lines).strip()
                cleaned_pandas_code = state["cleaned_pandas_code"]
                logger.info(f"cleaned_pandas_code {cleaned_pandas_code}")
                return state
        
        def pyspark_code_generator_node(self, state: AgentState) -> AgentState:
                # Dummy code generation based on task
                task_description = state.get("task_description", "")
                dfs = state.get("selected_dataframes", "")
                df_names = state.get("selected_dataframe_names", "")
                pandas_code = state.get("cleaned_pandas_code", "")
                logger.info(f"pandas_code {pandas_code}")
                spark_query = get_sparktool_prompt(dfs, df_names, task_description, pandas_code)
                # Generate code using LLM
                response = self.agent.invoke(spark_query)
                generated_pyspark_code = response.content.strip()
                state["generated_pyspark_code"] = generated_pyspark_code
                return state
        
        def code_checker_node(self, state: AgentState) -> AgentState:
                """
                Checks aliases used in DataframeInformation.update calls.
                If alias not present in loaded_dataframes, change .update(...) to .create(...).

                Returns updated code string.
                """
                generated_pandas_code = state.get("generated_pandas_code", "")
                generated_pyspark_code = state.get("generated_pyspark_code", "")
                
                # Auto-correct common LLM hallucination where it writes df.update(...) instead of DataframeInformation.update(...)
                generated_pandas_code = re.sub(r'\b[a-zA-Z0-9_]+\.update\s*\(\s*alias\s*=', 'DataframeInformation.update(alias=', generated_pandas_code)
                generated_pyspark_code = re.sub(r'\b[a-zA-Z0-9_]+\.update\s*\(\s*alias\s*=', 'DataframeInformation.update(alias=', generated_pyspark_code)

                loaded_dataframes = state.get("dataframes", "")
                pattern = re.compile(
                        r'DataframeInformation\.update\s*\(\s*alias\s*=\s*["\']([^"\']+)["\']\s*,\s*dataframe\s*=\s*([^\)]+)\)', 
                        flags=re.DOTALL
                )

                def replacer(match):
                        alias = match.group(1)
                        dataframe_expr = match.group(2).strip()
                        if alias not in loaded_dataframes:
                                # Replace with create(id=alias, alias=alias, dataframe=dataframe_expr)
                                return f'DataframeInformation.create(id="{alias}", alias="{alias}", dataframe={dataframe_expr})'
                        else:
                                # Keep original
                                return match.group(0)

                cleaned_pandas_code = pattern.sub(replacer, generated_pandas_code)
                state["cleaned_pandas_code"] = cleaned_pandas_code
                logger.info(f"cleaned_pandas_code {cleaned_pandas_code}")
                cleaned_pyspark_code = pattern.sub(replacer, generated_pyspark_code)
                logger.info(f"cleaned_pyspark_code {cleaned_pyspark_code}")
                state["cleaned_pyspark_code"] = cleaned_pyspark_code
                return state
        
        def _build_graph(self):
                graph_builder = StateGraph(AgentState)

                graph_builder.add_node("start", self.start_router)
                graph_builder.add_node("get_dataframes", self.get_dataframes_node)
                graph_builder.add_node("select_dataframe", self.select_dataframe_node)
                graph_builder.add_node("pandas_code_generator", self.pandas_code_generator_node)
                graph_builder.add_node("pandas_code_cleaner", self.pandas_code_cleaner_node)
                graph_builder.add_node("pyspark_code_generator", self.pyspark_code_generator_node)
                graph_builder.add_node("check_code", self.code_checker_node)

                graph_builder.add_edge("start", "get_dataframes")
                graph_builder.add_edge("get_dataframes", "select_dataframe")
                graph_builder.add_edge("select_dataframe", "pandas_code_generator")
                graph_builder.add_edge("pandas_code_generator", "pyspark_code_generator")
                graph_builder.add_edge("pyspark_code_generator", "check_code")
                graph_builder.add_edge("check_code", "pandas_code_cleaner")
                graph_builder.add_edge("pandas_code_cleaner", END)

                graph_builder.set_entry_point("start")
                return graph_builder.compile()
        
        @Logger.generate
        def pytool_executor(self, chat_id, user_id, session, task, result, langchain_utils, agent_name="pytool"):
                """
                Executes the provided task using a primary tool and a secondary Spark tool, and updates the result with the processed data.

                Args:
                        chat_id (str): The ID of the chat session.
                        user_id (str): The ID of the user initiating the request.
                        session (Session): The session object used for database operations.
                        task (str): The task to be processed by the primary tool.
                        result (dict): The dictionary containing results from previous processing stages.
                        agent (Agent): The primary tool agent used to process the task.
                        sparktoolAgent (Agent): The secondary Spark tool agent used for additional processing.
                        agent_name (str, optional): The name of the agent used, default is "pytool".

                Returns:
                        tuple: A tuple containing:
                        - dict: The updated result dictionary with tool observations.
                        - dict: The final processed result from the secondary tool, or None if processing failed.

                Raises:
                        Exception: If any error occurs during the execution or processing of the task.
                """
                try:    
                        # removing tool result and keeping only pytool result
                        logger.info(f"in pytool_executor {chat_id,user_id,session,task,result,langchain_utils,agent_name}")
                        
                        result = {key: value for key, value in result.items() if key == 'pytool'}
                        
                        graph = self._build_graph()
                        initial_state: AgentState = {
                                "dataframes": {},
                                "selected_dataframes": None,
                                "selected_dataframe_names": "",
                                "task_description": task,
                                "generated_pandas_code": "",
                                "generated_pyspark_code": "",
                                "cleaned_pandas_code": "",
                                "cleaned_pyspark_code": "",
                                }
                        resp = graph.invoke(initial_state)
                        logger.info(f"resp {resp}")
                        pandas_code = resp["cleaned_pandas_code"]
                        df = resp["selected_dataframes"]
                        df_alias = resp["selected_dataframe_names"]
                        logger.info(f"task {task}")
                        logger.info(f"code {pandas_code}")
                        LLMChatBot(user_id, chat_id, session).store_response(task, pandas_code)
                        #pandas_code = extract_code(code)
                        steps = CommonUtils.extract_steps(pandas_code)
                        #spark_query=get_sparktool_prompt(code)
                        #spk_code=self.spkagent.invoke(spark_query)
                        #spk_code=spk_code.content
                        spk_code=resp["cleaned_pyspark_code"]
                        logger.info(f"spk_code {spk_code}")
                        logger.info(f"df {type(df)}")
                        resp=DataEngineeringWrapper().pytool(pandas_code,user_id,chat_id,session,spk_code, df, df_alias, self.df_info)
                        #resp=json.dumps(resp)
                        logger.info(f"resp {resp}")
                        #wrapper_result_observation=json.loads(resp)
                        if isinstance(resp, str):
                                wrapper_result_observation = json.loads(resp)
                        else:
                                wrapper_result_observation = resp
                        logger.info(f"wrapper_result_observation {wrapper_result_observation}")
                        wrapper_text=wrapper_result_observation["result"].get('text')
                        logger.info(f"wrapper_text {wrapper_text}")
                        if wrapper_result_observation["success"]:
                                wrapper_result=wrapper_result_observation["result"]
                                logger.info(f"wrapper_result {wrapper_result}")
                        if wrapper_result_observation["result"]["success"]:
                                wrapper_text=langchain_utils.get_code_summary(pandas_code.replace('"', "'"))
                                message_text=f"""User task: {task}
                                Tool Response
                                {pandas_code}
                                Tool Result: {wrapper_text}"""
                        else:
                                message_text=f"""User task: {task}
                                Tool Response
                                {pandas_code}
                                Tool Result: {wrapper_text}"""
                                suggestion = langchain_utils.get_suggestion(message_text)
                                message_text = message_text + suggestion
                        logger.info(f"message_text {message_text}")
                        if "observation" in result[agent_name]:
                                result[agent_name]["observation"].append(message_text)
                        else:# pragma: no cover
                                result[agent_name]["observation"]=[message_text]
                        logger.info(f"pytool executor - result,wrapper_result: {result},{wrapper_result}")
                        return result,wrapper_result
                except Exception as e: # pragma: no cover
                        logger.error("An error occurred: %s", e, exc_info=True)
                        result[agent_name]['observation']=[f"Pytool agent failed with following error: {e}"]
                        return result, None
                        

