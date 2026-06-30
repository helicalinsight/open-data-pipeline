
from ........logger.logger import Logger, logger
from langchain_classic.chains.conversation.memory import ConversationBufferMemory
from .memory_model import MemoryModel


class Memory(MemoryModel):
    def __init__(self, session=None):
        try:
            super().__init__(session)
            logger.info("init")
            self.session=session
        except Exception as e:
            logger.error(f"Error initializing Memory: {str(e)}", exc_info=True)
            raise Exception(f"Error initializing Memory: {str(e)}") from e
    
    def update(self, input, output, memory, history, chat_id):
        """
        Store the metadata in the chatbot's memory.
        """
        try:
            logger.info("Storing response to memory")
            logger.info(f"Input: {input}")
            logger.info(f"Output: {output}")

            logger.info(f"memory.buffer {memory.buffer}")
            memory.save_context({"input": input}, {"output": output})
            logger.info(f"Saved to memory buffer: {memory.buffer}")
            super().save_memory(chat_id, history)
            logger.info(f"history {history}")
           
             
        except Exception as e:
            logger.error(f"Error storing response in memory: {str(e)}", exc_info=True)

    def get(self, chat_id):
        history = super().load_memory(chat_id)
        return history
