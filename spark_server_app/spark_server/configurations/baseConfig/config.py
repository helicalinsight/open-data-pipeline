import os
import configparser

from dotenv import load_dotenv

load_dotenv()

CUR_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class localDirectory():
    config = configparser.ConfigParser()
    if os.getenv("APP_ENVIRONMENT") == "prod":
        config_file = os.path.join(
            CUR_DIR_PATH, "../config","config-prod.ini")
    elif os.getenv("APP_ENVIRONMENT") == "dev":
        config_file = os.path.join(
            CUR_DIR_PATH,"../config","config-dev.ini")
    else:
        config_file = os.path.join(
            CUR_DIR_PATH, "../config","config-local.ini")
    config.read(config_file)
    
    BASE_DIR = config["storage"]["base_dir_storage"]
    UPLOAD_FOLDER = config["storage"]["upload_folder"]
    _path= os.path.join(BASE_DIR,UPLOAD_FOLDER)

    
class LogConfig():
    config = configparser.ConfigParser(interpolation=None)
    if os.getenv("APP_ENVIRONMENT") == "prod":
        config_file = os.path.join(
            CUR_DIR_PATH, "../logs", "log_config_prod.ini")
    elif os.getenv("APP_ENVIRONMENT") == "dev":
        config_file = os.path.join(
            CUR_DIR_PATH, "../logs","log_config_dev.ini")
    else:
        config_file = os.path.join(
            CUR_DIR_PATH, "../logs", "log_config_test.ini")
    config.read(config_file)
