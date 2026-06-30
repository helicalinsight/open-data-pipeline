#!/bin/bash
set -e
echo "updating configuration"
CONFIG_FILE_PATH=src/configurations/config/config-${APP_ENVIRONMENT}.ini
echo $CONFIG_FILE_PATH

# LLM config
if [ "$LLM_EXECUTION_MODE" = "apiserver" ]; then
    if [ -z "$LLM_BASE_URL" ] || [ -z "$LLM_API_KEY" ]; then
        echo "Error: LLM_BASE_URL and LLM_API_KEY environment variables are required when LLM_EXECUTION_MODE is set to 'apiserver'." >&2
        exit 1
    fi
    sed -i "/\[llm\]/,/^$/ s|base_url =.*|base_url = ${LLM_BASE_URL//\//\\/}/${LLM_API_KEY}|" $CONFIG_FILE_PATH
else
    sed -i "/\[llm\]/,/^$/ s/base_url =.*/base_url = ${OLLAMA_IP//\//\\/}:11434/" $CONFIG_FILE_PATH
fi

# Ollama Config
sed -i "/\[ollama\]/,/^$/ s/ollama_host_url =.*/ollama_host_url = ${OLLAMA_IP//\//\\/}:11434/" $CONFIG_FILE_PATH

## Storage
sed -i "/\[storage\]/,/^$/ s/base_dir_storage =.*/base_dir_storage = hadoop_local/" $CONFIG_FILE_PATH
sed -i "/\[storage\]/,/^$/ s/upload_folder =.*/upload_folder = upload/" $CONFIG_FILE_PATH


## AIRFLOW 
sed -i "/\[airflow\]/,/^$/ s/url =.*/url = open_data_pipeline_airflow_webserver:8080/" $CONFIG_FILE_PATH
sed -i "/\[airflow\]/,/^$/ s/spark_path =.*/spark_path = spark_server_app\/main.py/" $CONFIG_FILE_PATH
sed -i "/\[airflow\]/,/^$/ s/helper_module=.*/helper_module= inbuilt_modules\/helper\/helper.zip/" $CONFIG_FILE_PATH
sed -i "/\[airflow\]/,/^$/ s/username =.*/username = $AIRFLOW_USERNAME/" $CONFIG_FILE_PATH
sed -i "/\[airflow\]/,/^$/ s/password =.*/password = $AIRFLOW_PASSWORD/" $CONFIG_FILE_PATH
pip install uv
uv pip install --system -r src/requirements.txt
cd inbuilt_modules/helper
uv pip install --system .
uv pip install --system -q -r requirements.txt
cd ../../

echo "updated config.. running app"

echo "Installing  Firebird.. running app"
apt install -y wget
apt install -y libncurses6
apt install -y libtommath1
wget https://github.com/FirebirdSQL/firebird/releases/download/v5.0.1/Firebird-5.0.1.1469-0-linux-x64.tar.gz
tar -xvf Firebird-5.0.1.1469-0-linux-x64.tar.gz
cd Firebird-5.0.1.1469-0-linux-x64/
apt install -y procps
apt install -y libicu-dev
echo -e "\n" | ./install.sh
cd ../

exec "$@"


