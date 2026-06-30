import re
from langchain_classic.memory import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from .prompt import Prompt
from ....exceptions.exceptions import UtilityException
from ....logger.logger import Logger, logger


class Utils:
    def convert_from_mongo_history(self, mongo_history):
        history = ChatMessageHistory()
        try:
            if mongo_history != []:
                for step in mongo_history:
                    history.add_user_message(step["user"])
                    history.add_ai_message(step["ai"])
        except KeyError as e:
            logger.error(f"{e}", exc_info=True)
            raise KeyError("Missing key in mongo_history item.")
        except Exception as e:
            logger.error(f"{e}", exc_info=True)
            raise UtilityException("Unexpected error occurred in convert_from_mongo_history") from e
        return history

    def load_history(self, prompt, mongo_history):
        try:
            history = self.convert_from_mongo_history(mongo_history)
            if history.messages == []:
                history.add_user_message(prompt)
                history.add_ai_message("")
        except Exception as e:
            logger.error(f"{e}", exc_info=True)
            raise UtilityException("Unexpected error occurred in load_history") from e
        return history

    def generate_mongo_history(self, history):
        message_pairs = []
        try:
            for i in range(0, len(history.messages), 2):
                human_message = history.messages[i].content if isinstance(history.messages[i], HumanMessage) else None
                ai_message = history.messages[i + 1].content if i + 1 < len(history.messages) and isinstance(history.messages[i + 1], AIMessage) else None
                if human_message is not None and ai_message is not None:
                    message_pairs.append({"user": human_message, "ai": ai_message})
        except IndexError as e:
            logger.error(f"{e}", exc_info=True)
            raise IndexError("IndexError in generate_mongo_history.")
        except Exception as e:
            logger.error(f"{e}", exc_info=True)
            raise UtilityException("Unexpected error occurred in generate_mongo_history") from e
        return message_pairs
    
    def extract_code(self, response):
        try:
            match = re.search(r'<code>(.*?)</code>', response, re.DOTALL)
            if match:
                return match.group(1).strip()  # Return the code with <code> tags
            else:
                return "No code found within <code> tags."
        except re.error as e:
            logger.error(f"{e}", exc_info=True)
            raise re.error("Regex error occurred in extract_code")
        except Exception as e:
            logger.error(f"{e}", exc_info=True)
            raise UtilityException("Unexpected error occurred in extract_code") from e
        return "Error extracting code."
