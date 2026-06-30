from ..logger.logger import Logger
from ..connectors.mongo_operations import MongoOperations
import yaml

log = Logger
mongo_ops = MongoOperations()


class Config:

    @log.generate
    def get(self, chat_id, user_id):
        history = mongo_ops.get_history_chat_and_user(chat_id, user_id)
        history_json = {"pipeline": history}
        history_dict = self.convert_to_yml(history_json)
        history_dict.update({"user_id": user_id})
        history_dict.update({"chat_id": user_id})
        return history_dict

    @log.generate
    def convert_to_yml(self, history):
        history_yml = yaml.dump(history, default_flow_style=False, indent=2)  # converts json to yml
        history_dict = yaml.safe_load(history_yml)  # converts yml to python object
        return history_dict
