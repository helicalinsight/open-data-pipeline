import pytest
from deepeval import evaluate, test_case
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from src.models.connector import MongoConnector
import re, os
import json
from typing import Any, Optional, Type, List
from pydantic import BaseModel
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.metrics.answer_relevancy.schema import AnswerRelevancyScoreReason, Statements, Verdicts
from src.core.llm import get_chat_model, LLMConfig
from src.api.services.langchain_service.fallback_executor import *
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.engineer import DataEngineer

# --- Helper Functions ---

def _clean_json_content(content: str) -> str:
    #return re.sub(r"^```json\s*|```$", "", content.strip(), flags=re.MULTILINE).strip()
    # Remove surrounding ```json ... ```
    content = re.sub(r"^```json\s*|```$", "", content.strip(), flags=re.MULTILINE).strip()
    # Fix invalid escape sequences (like \')
    content = re.sub(r'\\(?!["\\/bfnrtu])', '', content)
    return content

# --- Custom Evaluation Model ---

class CustomOllamaModel(DeepEvalBaseLLM):
    def __init__(self, model_name="deepseek-coder-v2"):
        self.model_name = model_name
        self.llm = get_chat_model(
            LLMConfig(model=model_name, base_url="http://57.128.161.235:11434")
        )

    def load_model(self, *args, **kwargs):
        return self.llm

    def get_model_name(self):
        return self.model_name

    def generate(self, prompt: str, schema: Optional[Type[BaseModel]] = None, **kwargs) -> Any:
        response = self.llm.invoke(prompt)
        content = self._extract_content(response)

        if schema == Statements:
            return Statements(statements=[content])
        if schema == Verdicts:
            try:
                cleaned_content = _clean_json_content(content)
                return Verdicts(**json.loads(cleaned_content))
            except Exception as e:
                raise ValueError(f"Could not parse Verdicts schema. Raw: {content}\nError: {e}")
        if schema == AnswerRelevancyScoreReason:
            return AnswerRelevancyScoreReason(reason=content)

        return content

    async def a_generate(self, prompt: str, schema: Optional[Type[BaseModel]] = None, **kwargs) -> Any:
        response = await self.llm.ainvoke(prompt)
        content = self._extract_content(response)

        if schema == Statements:
            return Statements(statements=[content])
        if schema == Verdicts:
            try:
                cleaned_content = _clean_json_content(content)
                return Verdicts(**json.loads(cleaned_content))
            except Exception as e:
                raise ValueError(f"Could not parse Verdicts schema. Raw: {content}\nError: {e}")
        if schema == AnswerRelevancyScoreReason:
            return AnswerRelevancyScoreReason(reason=content)

        return content

    def _extract_content(self, response: Any) -> str:
        if isinstance(response, dict) and "content" in response:
            return response["content"]
        elif hasattr(response, "content"):
            return response.content
        else:
            return str(response)

@pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="Skipping in non-test environment")
@pytest.mark.parametrize("test_case", [
    {
        "task": "split name column using left most delimiter",
        "expected_summary": "The 'name' column is split using the leftmost delimiter, and the first segment is retained."
    },
    {
        "task": "Create current_timestamp column with current time",
        "expected_summary": "A new column 'current_timestamp' is added with the current timestamp for each row."
    },
    {
        "task": "if Age is <= 25 then mark as 'young', if Age > 30 then mark as 'old' else 'middle'",
        "expected_summary": "A new column is created marking age groups as 'young', 'middle', or 'old' based on age conditions."
    },
    {
        "task": "delete all the records which starts with XX from order_id column",
        "expected_summary": "Deleted all the rows where 'order_id' column starts with 'XX'."
    },
    {
        "task": "extract week number from order_date column",
        "expected_summary": "The week number is extracted from the 'order_date' column."
    },
    {
        "task": "calculate difference in weeks between order_date and ship_date column",
        "expected_summary": "Calculates the difference in weeks between 'order_date' and 'ship_date' columns."
    },
    {
        "task": "extract week number from ship_date column",
        "expected_summary": "The week number is extracted from the 'ship_date' column."
    },
    {
        "task": "change order_date date format as per american standard",
        "expected_summary": "The 'order_date' column's date format is converted to the American standard (MM/DD/YYYY)."
    },
    {
        "task": "drop the column which has one null records in it.",
        "expected_summary": "Dropped the columns that contain exactly one null record."
    },
    {
        "task": "replace XXXXXX with $ in all columns of 2017_Order_Data",
        "expected_summary": "Replaces all occurrences of 'XXXXXX' with '$' in all columns of '2017_Order_Data'."
    },
    {
        "task": "Cast all columns to string",
        "expected_summary": "Converts all the columns data types to string data type."
    },
    {
        "task": "Remove spaces from all the data",
        "expected_summary": "Removes spaces from all string data in the DataFrame."
    },
    {
        "task": "rename all the column names using - instead of _",
        "expected_summary": "Renames all columns replacing underscores '_' with dashes '-'."
    },
    {
        "task": "fill city column with different random city name of india",
        "expected_summary": "Fills the 'city' column with random city names from India."
    },
    {
        "task": "Remove all records where order_id contains XXXXXX",
        "expected_summary": "Deletes all rows where 'order_id' contains the substring 'XXXXXX'."
    },
    {
        "task": "calculate date difference in days between todays current date and ship_date",
        "expected_summary": "Calculates the number of days between today's date and the 'ship_date' column."
    },
    {
        "task": "find data difference between current date and ship_date",
        "expected_summary": "Calculates the difference between the current date and 'ship_date'."
    },
    {
        "task": "add a column with todays date in 2017 order data",
        "expected_summary": "Adds a column with today's date to the 2017 order data."
    },
    {
        "task": "show me all the records where worm_instance is null",
        "expected_summary": "Returns all records where 'worm_instance' column is null."
    },
    {
        "task": "give me all the distinct values from customer_id column",
        "expected_summary": "Retrieves all distinct values from the 'customer_id' column."
    },
    {
        "task": "cast order_id column to string",
        "expected_summary": "Converts the 'order_id' column to string type."
    },
])

def test_langgraph_pipeline_summary(test_case):
    mongo_connector = MongoConnector()
    mongo_client = mongo_connector.client
    session = mongo_client._Database__client.start_session()
    user_id = '6619156aa5f4c5c1b01e4d07'
    chat_id = '65cb43f2007a5f38718b9d6a'

    pytool_agent = DataEngineer.create_agent("pytool")
    agent = pytool_agent(user_id, chat_id, session).agent

    spark_agent = DataEngineer.create_agent("sparktool")
    spkagent = spark_agent(user_id, chat_id, session).agent

    evaluation_model = CustomOllamaModel()

    graph = FallBackExecutor(user_id, chat_id, session, agent, spkagent)._build_graph()
    initial_state = {
                                "dataframes": {},
                                "selected_dataframe": None,
                                "selected_dataframe_name": "",
                                "task_description": test_case["task"],
                                "generated_pandas_code": "",
                                "cleaned_code": "",
                                "generated_pyspark_code": "",
                                }
    final_state = graph.invoke(initial_state)
    # Generate explanation
    description_prompt = f"Describe what this code does:\n{final_state['generated_pandas_code']}"
    nl_summary = evaluation_model.generate(description_prompt)

    # Build test case
    deepeval_case = LLMTestCase(
        input=test_case["task"],
        actual_output=nl_summary,
        expected_output=test_case["expected_summary"]
    )

    metric = AnswerRelevancyMetric(
        model=evaluation_model,
        threshold=0.6,
        include_reason=True
    )

    results, _ = evaluate([deepeval_case], [metric])
    test_results = results[1]
    for test_result  in test_results:
        for metric in test_result.metrics_data:
            assert metric.score >= metric.threshold, (
                f"Test failed: score={metric.score:.2f} below threshold={metric.threshold}. "
                f"Task: {test_case['task']}\nReason: {metric.reason}"
            )
