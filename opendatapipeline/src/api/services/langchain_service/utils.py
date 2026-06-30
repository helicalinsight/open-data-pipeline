from datetime import date, datetime
import difflib
import re
from .odpgraph.llm_prompts.intent_prompt import intent_list
from .odpgraph.odpchain.query_generator import QueryGenerator
from .odpgraph.llm_prompts.code_summary_prompt import get_code_summary_prompt
from ....logger.logger import logger, Logger


class LangchainServiceUtils:
    def __init__(self, session, llm):
        """
        Initializes the LangchainServiceUtils instance.

        Args:
            session (Session): The session object used for database operations.
            llm (LLM): The language model instance used for generating queries.
        """
        self.session=session
        self.llm = llm

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
        

    def match_string(self, input_string):
        """
        Finds the closest match for the input string from a predefined list of intents.

        Args:
            input_string (str): The string to match against the intent list.

        Returns:
            str: The best matching string from the intent list, or 'analysis' if no match is found.
        """
        lis=intent_list
        best_match = difflib.get_close_matches(input_string, lis, n=1, cutoff=0.6)
        if best_match:
            return best_match[0]
        else:
            return 'analysis'
        
    def sql_generator(self, input_prompt,chat_id):
        """
        Generates a SQL query based on the input prompt and chat ID.

        Args:
            input_prompt (str): The prompt to generate the SQL query from.
            chat_id (str): The chat ID used to generate expected output.

        Returns:
            str: The generated SQL query.
        """
        prompt=QueryGenerator(self.session).generate_expected_output(input_prompt,chat_id)
        complete_query = prompt

        response = self.llm.invoke(complete_query)
        return response.content


    def get_code_summary(self,code):
        prompt = get_code_summary_prompt(code)
        response = self.llm.invoke(prompt)
        return response.content.replace('"', "'")
        

    def regex_matcher(self, resp):
        """
        Extracts the SQL query from a response string using regex.

        Args:
            resp (str): The response string containing the SQL query.

        Returns:
            str or None: The extracted SQL query, or None if no query is found.
        """
        match = re.search(r"```sql\n(.*?)\n```", resp, re.DOTALL)

        if match:
            sql_query = match.group(1)
            sql_query=sql_query.replace("\n"," ")
            return sql_query
        else:
            match = re.search(r"\bSELECT\b.*?;", resp, re.IGNORECASE | re.DOTALL)

            if match:
                sql_query = match.group(0)
                sql_query=sql_query.replace("\n"," ")
                return sql_query
            else:
                return None
    
    def get_suggestion(self, message):
        complete_query = message + """
Suggested user task rule:
- Generated the suggested user task in a non technical way.
- The suggested user task should not have any logical issue.
- It should be complete and concise.
- Carefully analyze the above message to best of your knowledge and include the possible suggestion in the output.
Generate the output in the below format:
```
"Try this task": {{suggested User Task}}
```
"""
        response = self.llm.invoke(complete_query)
        return response.content
