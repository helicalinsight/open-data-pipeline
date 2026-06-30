from datetime import date, datetime, timezone
import json
import re
import uuid

from src.exceptions.exception import RateLimitException,LangchainServiceException
from src.core.llm import get_chat_model
from ....logger.logger import logger, Logger
# from graphviz import Graph
from langgraph.graph import StateGraph, START, END
from .odpgraph.llm_prompts.intent_prompt import intent_prompt
from .odpgraph.odpchain.agents.dataengineering.engineer import DataEngineer
from ....models.mongo.mongo_langchain import MongoLangchain
from ....models.mongo.mongo_factory import MongoFactory
from .utils import LangchainServiceUtils
from ....models.connector import MongoConnector

from .odpgraph.odpchain.agents.dataengineering.tools.pytool.prompt import get_pytool_prompt
from .odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from .fallback_executor import FallBackExecutor
from ..pyspark_service.llm_chatbot import LLMChatBot
from ..pyspark_service.router_agent import RoutingAgent
#from ..pyspark_service.data_analyst_agent import DataAnalystAgent
from ..pyspark_service.pytool_agent import *
#from ..pyspark_service.pytool_agent_copy import PyToolAgent
#from ..pyspark_service.math_agent import MathAgent


class LangchainService:
    def __init__(self, session) -> None:
        """
        Initializes the LangchainService instance.

        Args:
            session (Session): The session object used for database operations.
        """
        logger.info("Initializing Session")
        self.session = session
        self.chat_collection = MongoFactory(MongoConnector().client, "chats", self.session)
        self.llm = get_chat_model()

    def json_serial(self, obj):
        """
        JSON serializer for objects not serializable by default JSON code.

        Args:
            obj (object): The object to be serialized.

        Returns:
            str: The ISO format string representation of the datetime or date object if applicable.

        Raises:
            TypeError: If the object is not of a serializable type.
        """

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

    def plannerAgent(self, input_1):
        """
        Placeholder method for processing input tasks. Currently, it just returns the input.

        Args:
            input_1 (str): The input string to be processed.

        Returns:
            str: The same input string that was provided.
        """
        logger.info(f"Planner agent Input: {input_1}")
        # complete_query = planner + input_1
        # ls=input_1.split("||")
        # response_update=str(ls)
        # response = llm.invoke(complete_query)
        
        # response_update=str(ls)
        # return response.content
        return input_1
    
    @Logger.generate
    def agent_identifier(self, input_2,config):# pragma: no cover
        """
        Identifies the appropriate agent based on the input and config, processes tasks, and handles exceptions.

        Args:
            input_2 (str): The input task to be identified and processed.
            config (dict): Configuration dictionary containing "user_id" and "chat_id".

        Returns:
            list: A list containing two elements:
                - dict: Results of agent processing.
                - object: Wrapper result containing additional details.
        """
        logger.info("in agent_identifier")
        langchain_utils = LangchainServiceUtils(self.session, self.llm)
        input_task=[]
        result={}
        wrapper_result=None
        agent_intent_logic=None
        result_response=[]
        input_task.append(input_2)
        # Regular expression pattern to match text inside square bracket
        
        # Using re.findall to extract text inside square brackets
        # extracted_text = re.findall(r'\[.*?\]', input_2)
        # if extracted_text:
        #     input_2=eval(extracted_text[0])
        #     input_2 = [item for item in input_2 if item.strip()]
        # else:
        #     input_2=[]
        count_dict = {}
        user_id=config["configurable"]["user_id"]
        chat_id=config["configurable"]["chat_id"]
        
        for task in input_task:
            logger.info(f"Current Task: {task}")
            task_copy = task[:] #creates a task copy
            try:
                complete_query = intent_prompt + task
                response = self.llm.invoke(complete_query)
                logger.info(f"response {response}")
                try:
                    raw_content = response.content.strip()
                    if "```json" in raw_content:
                        match = re.search(r"```json\s*(.*?)\s*```", raw_content, re.DOTALL)
                        raw_content = match.group(1) if match else raw_content.strip()
                    elif "```" in raw_content:
                        match = re.search(r"```\s*(.*?)\s*```", raw_content, re.DOTALL)
                        raw_content = match.group(1) if match else raw_content.strip()
                    
                    agent_info=json.loads(raw_content)
                    agent_name = agent_info["intent"]
                    #logger.info(f"agent_name {agent_name}")
                    #if agent_name == "misc":
                    #    LLMChatBot(user_id,chat_id,self.session).invoke_agent(task)

                    agent_intent_logic = agent_info["extra_info"]
                except Exception as e:
                    logger.error("Error in identifying the Agent. Considering pytool. Error: %s", e, exc_info=True)
                    agent_name = "pytool"
                    agent_intent_logic = None
                agent_name=langchain_utils.match_string(agent_name)
                logger.info(f"agent_name {agent_name}")
                if agent_name=="CurrentWorkingFile":
                    agent_name="cwf"
                if agent_name=='replace':
                    agent_name="replace_special_characters"
                if agent_name=='correlation':
                    agent_name="sql_operations"
                if agent_name=="rename":
                    agent_name="rename_columns"
                if agent_name=="analysis":
                    agent_name="sql_operations"
                    resp=langchain_utils.sql_generator(task,chat_id)
                    task=langchain_utils.regex_matcher(resp)
                    
                if agent_name=="fill_null":
                    agent_name="pytool"
                    
                logger.info(f"Current Agent Name: {agent_name}")
                agentobject= DataEngineer.create_agent(agent_name)
                agent=agentobject(user_id,chat_id, self.session).agent
                if agent_name in result:
                        count_dict[agent_name] += 1
                        new_key = f"{agent_name}_{count_dict[agent_name]}"
                        result[new_key] = {}
                        agent_name=new_key
                else:
                        result[agent_name] = {}
                        count_dict[agent_name] = 0
                        agent_name=agent_name
                    
                
                if agent_name=="pytool":
                    sparkAgent= DataEngineer.create_agent("sparktool")
                    spkAgent=sparkAgent(user_id,chat_id, self.session).agent
                    result,wrapper_result=FallBackExecutor(user_id, chat_id, self.session, agent, spkAgent).pytool_executor(chat_id,user_id,self.session,task,result,langchain_utils)
                else:
                    try:
                        logger.info(f"task: {task}")
                        for chunk in agent.stream({"input": task}):
                        # Agent Action
                            logger.info(f"chunk: {chunk}")
                            if "steps" in chunk:
                                for step in chunk["steps"]:
                                    logger.info(f"step:{step}")
                                    wrapper_result_observation=step.observation
                                    try:
                                        wrapper_result_observation=json.loads(wrapper_result_observation)
                                    except:
                                        raise Exception(step.observation)
                                    logger.info(f"Return Observation: {wrapper_result_observation}")
                                    
                                    wrapper_text=wrapper_result_observation["result"].get('text')
                                    tool_success=wrapper_result_observation["result"].get('success')
                                    if tool_success == False:
                                        raise Exception(wrapper_text)
                                    if wrapper_result_observation["success"]:
                                        wrapper_result=wrapper_result_observation["result"]
                                    message_text=f"Tool Result: `{wrapper_text}`"
                                    if "observation" in result[agent_name]:
                                        result[agent_name]["observation"].append(message_text)
                                    else:
                                        result[agent_name]["observation"]=[message_text]
                                    LLMChatBot(user_id, chat_id, self.session).store_response(task, message_text)
                                        
                            # Final result
                            elif "output" in chunk:
                                ### Occasionally we get only output without observation. So to handle that added the below code. 
                                # if "observation" not in chunk:
                                #    raise Exception("Agent could not perform the task!")
                                message_text=f'Final Output: {chunk["output"]}'
                                logger.info(f"message_text: {message_text}")
                                result[agent_name]["final"]=message_text
                                ### In somecase we are not receiving observation and because of which agent is not able to execute but has some messages on how the task has to be done. Sending these as observations
                                if "observation" not in result[agent_name]:
                                    result[agent_name]["observation"]= [chunk["messages"]]

                            else:
                                pass
                    except Exception as e:
                        logger.error(f"{agent_name} - Tool failed with exception: %s", e, exc_info=True)
                        result[agent_name]["observation"]=[f"Tried to perform the task using the tool '{agent_name}' but got the following error: {e}. Retrying it using pytool"]
                        result["pytool"] = {}
                        logger.info("calling pytool")
                        agentobject= DataEngineer.create_agent("pytool")
                        agent=agentobject(user_id,chat_id, self.session).agent
                        sparkAgent= DataEngineer.create_agent("sparktool")
                        spkAgent=sparkAgent(user_id,chat_id, self.session).agent
                        result,wrapper_result=FallBackExecutor(user_id, chat_id, self.session, agent, spkAgent).pytool_executor(chat_id,user_id,self.session,task,result,langchain_utils)
                        logger.info(f"fallback pytool result, wrapper result: {result}, {wrapper_result}")

            except RateLimitException as e:
                logger.warning(f"Rate limit exception in agent_identifier: {str(e)}")               
                result = {"__rate_limit_error__": True, "message": str(e)}
                wrapper_result = None
                result_response = [result, wrapper_result, None]
                return result_response


            except Exception as e:
                logger.error("An error occurred: %s", e, exc_info=True)
                error_response = {
                    "success": False,
                    "msg": "Task processing failed due to Unable to identify the agent"
                }
                raise LangchainServiceException(error_response, 500)
        logger.info(f"Final Result, Wrapper result: {result}, {wrapper_result}")
        result_response.append(result)
        result_response.append(wrapper_result)
        result_response.append(agent_intent_logic)
        return  result_response
    
    @Logger.generate
    def response_generator(self, result_response): # pragma: no cover
        """
        Generates a combined response based on the results of the agent processing.

        Args:
            result_response (list): A list containing the results of agent processing and wrapper result.

        Returns:
            tuple: A tuple containing:
                - str: The generated response message.
                - object: The wrapper result containing additional details or None.
        """
        try:
            logger.info(f"Response of langchain: {result_response}")
            input_3=result_response[0]
            wrapper_result=result_response[1]
            intent_message=result_response[2] if result_response[2] else ""

            # Check for rate limit error marker
            if isinstance(input_3, dict) and input_3.get("__rate_limit_error__"):
                error_message = input_3.get("message", "Rate limit exceeded")
                logger.warning(f"Rate limit error from agent_identifier: {error_message}")
                return f"Rate limit exceeded: {error_message}. Please try again later.", None

            logger.info(f"input_3 {input_3}")
            logger.info(f"intent_message {intent_message}")
            if input_3=={}:
                return "Please ensure that the task is provided correctly and in proper English format, as no task has been performed.",None
            else:
                try:
                    message = intent_message + '. '.join([value['observation'][0] for value in input_3.values()])
                    logger.info(f"message: {message}")
                    cleaned_message = re.sub(r'<code>|</code>|<steps>|</steps>', '', message).replace("category:", "User input category:").replace("alias:", "Dataframe used:").replace("steps:", "Tool steps:").replace("Code:", "Tool generated code:")
                    complete_query = cleaned_message + """
    You are a helpful assistant. You are an export in data engineering tasks. 
    Your task is to generate markdown output by first identifying all the sections from the above message. Do not miss any section from the message.
    If there are any errors, convert it to user-friendly message.
    Please provide the output in markdown format. Do not use headers instead use bolds. The Markdown elements you have access to are: bold, italic, links, tables, lists, code blocks, and blockquotes. 

    ####
    {{response}}
    ####
    """
                    response = self.llm.invoke(complete_query)
                    logger.info(f"response: {response}")
                    logger.info(f"response.content: {response.content}")
                    logger.info(f"wrapper_result: {wrapper_result}")
                    return response.content,wrapper_result
                    
                except Exception as e:
                        logger.error("An error occurred: %s", e, exc_info=True)
                        error_response = {
                            "success": False,
                            "msg": "An error occurred during the task. Please try again with a different prompt or rephrase the sentence."
                        }
                        raise LangchainServiceException(error_response, 500)
        except Exception as e:
            logger.error("Critical unexpected error in response_generator: %s", e, exc_info=True)
            error_response = {
                "success": False,
                "msg": "Response generation failed due to an unexpected system error"
            }
            raise LangchainServiceException(error_response, 500)    


    def routing(self, input_text,user_id,chat_id):
        logger.info("in routing")
        routing_output = RoutingAgent(user_id,chat_id,self.session).invoke_agent(input_text)
        logger.info(f"routing_output {routing_output}")
        #if routing_output != "data_transformation":
        #    return LLMChatBot(user_id, chat_id, self.session).invoke_agent(input_text)
        return routing_output
        
    def processs(self, input_text,user_id,chat_id): # pragma: no cover
        """
        Processes the input text through a workflow of agents, generates responses, and updates the database.

        Args:
            input_text (str): The input text to be processed.
            user_id (str): The ID of the user initiating the request.
            chat_id (str): The ID of the chat session.

        Returns:
            dict: A dictionary containing the success status and event details.
        """
        succ,chat_document=self.chat_collection.get_by_id(chat_id)
            
        workflow = StateGraph(object)
        dt = datetime.now(timezone.utc) 
        utc_time = dt.replace(tzinfo=timezone.utc) 
        timestamp = utc_time.timestamp() 

        workflow.add_node("plannerAgent", self.plannerAgent)
        workflow.add_node("agent_identifier", self.agent_identifier)
        workflow.add_node("response_generator", self.response_generator)
        
        workflow.add_edge('plannerAgent', 'agent_identifier')
        workflow.add_edge('agent_identifier', 'response_generator')
        workflow.add_edge(START, "plannerAgent")
        workflow.add_edge("response_generator", END)
        app = workflow.compile()

        resp,wrapper_result=app.invoke(input_text,{"configurable": {"user_id": user_id,"chat_id": chat_id}})
        message_id = str(uuid.uuid4())
        
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
        if wrapper_result is None:
            pass
        else:
            if 'source_id' in wrapper_result and "export_name" in wrapper_result:
                data_to_insert["messages"][0]["export"]=True
                data_to_insert["messages"][0]["details"]["export_details"]={"source_id":wrapper_result.get("source_id"),"export_name":wrapper_result.get("export_name")}
                
        MongoLangchain(MongoConnector().client, "langchain", self.session).create_or_update(data = data_to_insert)
        self.chat_collection.update_one(chat_id, "isChatMode", True )
    
        logger.info(f"Sending the Response back: {{'success':{True},'event':{data_to_insert}}}")
        return {"success":True,"event":data_to_insert}
    