from langchain_classic.agents import AgentExecutor, create_react_agent, Tool #, initialize_agent, AgentType
#from langchain_core.messages import HumanMessage
#from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.conversation.memory import ConversationBufferMemory
from src.core.llm import get_chat_model, LLMConfig
from langchain_core.tools import tool, StructuredTool
#from typing import Optional, Dict, Any
from ....logger.logger import Logger, logger
#from ..langchain_service.utils import LangchainServiceUtils
from ....models.mongo.mongo_langchain import MongoLangchain
from ....models.connector import MongoConnector
from ....models.mongo.mongo_factory import MongoFactory
#from langchain_classic.chains import LLMChain
from langchain_core.prompts import PromptTemplate
#import json
from typing import Final #, TypedDict
import uuid
#from .utils import Utils
from datetime import datetime, timezone #date, 
from ..langchain_service.odpgraph.odpchain.agents.memory.memory import Memory
from ..langchain_service.odpgraph.odpchain.agents.context.context import Context
from langgraph.graph import StateGraph, START, END #, StateGraph, MessagesState
from pydantic import BaseModel


CHAT_MEMORY: Final[str] = "chat_memory"

class PyToolInput(BaseModel):
    task_input: str
    df: dict


class PyToolAgent:
    def __init__(self, user_id, chat_id, session=None):
        try:
            logger.info("init")
            self.session=session
            self.user_id=user_id
            self.chat_id= chat_id
            
            self.chat_collection = MongoFactory(MongoConnector().client, "chats", self.session)
            self.llm = get_chat_model(LLMConfig(model="mixtral:latest"))
            self.context = Context(self.session)
            self.llm_memory = Memory(self.session)
            self.history = self.llm_memory.load_memory(self.chat_id)
            self.memory = ConversationBufferMemory(chat_memory=self.history)
        except Exception as e:
            logger.error(f"Error initializing PyToolAgent: {str(e)}", exc_info=True)
            raise Exception(f"Error initializing PyToolAgent: {str(e)}") from e
    
    def fetch_data(self, task, config):
        logger.info(f"in fetch_data {task} {config}")
        ddls = []
        df_dict = self.context.get_dataframes(self.chat_id)
        logger.info(f"df_dict {df_dict}")
        for table_name, df in df_dict.items():
            pass
        return df_dict
    
#    @tool(args_schema=PyToolInput)
    def run_pandas_tool(self, task_input: str, df: dict) -> Tool:
        """Returns a Tool object that will execute pandas code generation for a given task and dataframe."""
        #"""Generates pandas code based on user task and dataframe"""
        def pandas_executor(input_str: str) -> str:
            logger.info(f"task_input {input_str} {type(input_str)}")
            logger.info(f"df {df} {type(df)}")
            dataframe = list(df.values())[0]
            prompt = f"""
            You are a pandas expert. Use the provided sample dataframe and column data to generate pandas code for the user task.

Column names:
{list(dataframe.columns)}

Sample data (use this to infer delimiters, data types, etc.):
{dataframe.head(5).to_string(index=False)}

User task:
{task_input}

Instructions:
- Carefully examine the sample data provided to identify patterns, such as delimiters in columns.
- Do not assume anything.
- Generate pandas code that works for the given sample.
- Explain the steps you used to analyze the data and create the code.

Respond in this format:
Code: {{pandas code}}
Steps: {{steps used to generate the pandas code, including how you used the sample data}}
            """
            logger.info(f"prompt {prompt}")
            return self.llm.invoke(prompt)
        
        return Tool(
        name="PandasTool",
        func=pandas_executor,
        description="Generates pandas code based on user task and dataframe provided"
        )
    
    def generate_code_pytool(self, df, config):
        logger.info(f"in generate_code_pytool {df}")
        logger.info(f"config {config}")
        logger.info(f"config['metadata']['input'] {config['metadata']['input']}")
        input_task = config['metadata']['input']
        logger.info(f"input_task {input_task}")
        #tool = Tool(name="Pandas Expert", func=self.run_pandas_tool(config['metadata']['input'], df), description="Generates pandas code based on user task and dataframe")
        #logger.info(f"tool {tool}")
        tool = self.run_pandas_tool(input_task, df)
        tools =[tool]
        logger.info(f"tools {tools}")
        pandas_agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=PromptTemplate.from_template("""Answer the following question using the tools below.

You must use this format:
Thought: what you are thinking
Action: tool name (from: {tool_names})
Action Input: input to the tool

When you have the final answer:
Final Answer: your final answer here

Tools:
{tools}

Previous conversation:
{chat_history}

Question: {input}

{agent_scratchpad}"""
                )
            )
        logger.info(f"pandas_agent {pandas_agent}")
        agent_executor = AgentExecutor(agent=pandas_agent, tools=tools, memory=self.memory, verbose=True, handle_parsing_errors=True, max_iterations = 5)
        logger.info(f"agent_executor {agent_executor}")
        try:
            response = agent_executor.invoke({"input": input_task})
            logger.info(f"response {response}")
        except Exception as e:
            logger.error(f"Error in pandas_agent executor invoke: {str(e)}", exc_info=True)
        return response

    def process(self, input_task, user_id, chat_id):
        workflow = StateGraph(object)
        
        workflow.add_node("FetchData", self.fetch_data)
        workflow.add_node("GeneratePyToolCode", self.generate_code_pytool)
        
        workflow.add_edge('FetchData', 'GeneratePyToolCode')
        
        workflow.add_edge(START, "FetchData")
        workflow.add_edge("GeneratePyToolCode", END)
        app = workflow.compile()
        resp=app.invoke(input_task, {"configurable": {"user_id": user_id,"chat_id": chat_id, "input": input_task}})
        message_id = str(uuid.uuid4())
        dt = datetime.now(timezone.utc) 
        utc_time = dt.replace(tzinfo=timezone.utc) 
        timestamp = utc_time.timestamp()

        data_to_insert = {
                                "user_id": user_id,
                                "chat_id": chat_id,
                                "messages":[
                                    {"event" : "bot",
                                    "message_id" :message_id,
                                    "message": resp,
                                    "timestamp": timestamp,
                                    "export":False,
                                    "stage" : "final",
                                    "details":{"refresh":True}}
                                ]
                            }
        MongoLangchain(MongoConnector().client, "langchain", self.session).create_or_update(data = data_to_insert)
        self.chat_collection.update_one(chat_id, "isChatMode", True )
    
        return {"success":True,"event":data_to_insert}
        