
import os
from datetime import timedelta
import configparser
import os

from dotenv import load_dotenv

load_dotenv()
environment=os.environ.get("SERVER_ENVIRONMENT")

class SourceConfig():
    yml_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "datasources", "datasources.yml")
    python_md_file_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "features", "python_documentation.md")
    yaml_md_file_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "features", "yaml_documentation.md")
    application_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "features", "features.yml")
    job_args_help_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "features", "job_arguments_help.md")
    schedule_path = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "features", "schedule.yml")


class BaseConfig():
    #BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    BASE_DIR = os.path.join(os.path.abspath(os.path.join(__file__, "../../../../")))
    DAGS_PATH = os.getenv('AIRFLOW_HOME')
    config = configparser.ConfigParser()
    if os.getenv("APP_ENVIRONMENT") == "prod":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "config","config-prod.ini")
    elif os.getenv("APP_ENVIRONMENT") == "dev":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "config","config-dev.ini")
    else:
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "config","config-local.ini")
    config.read(config_file)
    BASE_DIR = config["storage"]["base_dir_storage"]
    UPLOAD_FOLDER = config["storage"]["upload_folder"]
    DAGS_PATH = os.getenv('AIRFLOW_HOME')
    if not DAGS_PATH:
        raise EnvironmentError("The AIRFLOW_HOME environment variable is not set.")


    SECRET_KEY = os.getenv('SECRET_KEY', "AskData")
    HASH_ALGORITHM = os.getenv("HASH_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


class Config():
    config = configparser.ConfigParser()
    if os.getenv("APP_ENVIRONMENT") == "prod":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "config","config-prod.ini")
    elif os.getenv("APP_ENVIRONMENT") == "dev":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "config","config-dev.ini")
    elif os.getenv("APP_ENVIRONMENT") == "test":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "config","config-test.ini")
    else:
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "config","config-local.ini")
    config.read(config_file)
    build_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "config","build.ini")
    config.read(build_file)


class LogConfig():
    config = configparser.ConfigParser(interpolation=None)
    if os.getenv("APP_ENVIRONMENT") == "prod":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "main_config","config-prod.ini")
    elif os.getenv("APP_ENVIRONMENT") == "dev":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "main_config","config-dev.ini")
    else:
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "main_config","config-local.ini")
    config.read(config_file)


class AirflowConfig():
    config = configparser.ConfigParser()
    if os.getenv("APP_ENVIRONMENT") == "prod":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "main_config","config-prod.ini")
    elif os.getenv("APP_ENVIRONMENT") == "dev":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "main_config","config-dev.ini")
    else:
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "main_config","config-local.ini")
    config.read(config_file)

class LangchainConfig():
    config = configparser.ConfigParser()
    if os.getenv("APP_ENVIRONMENT") == "prod":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "main_config","config-prod.ini")
    elif os.getenv("APP_ENVIRONMENT") == "dev":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "main_config","config-dev.ini")
    else:
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "main_config","config-local.ini")
    config.read(config_file)

class LlamaApiServerConfig():
    config = configparser.ConfigParser()
    if os.getenv("APP_ENVIRONMENT") == "prod":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "main_config","config-prod.ini")
    elif os.getenv("APP_ENVIRONMENT") == "dev":
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "main_config","config-dev.ini")
    else:
        config_file = os.path.join(os.path.abspath(os.path.join(__file__, "../../")), "main_config","config-local.ini")
    config.read(config_file)


