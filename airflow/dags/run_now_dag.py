from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
import pendulum

default_args = {'owner': 'airflow'}

with DAG(
    dag_id='run_now_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False,
    tags=['run_now_dag'],
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC")
) as dag:

    def get_conf(key, default=None):
        return "{{ dag_run.conf.get('" + key + "', '" + str(default) + "') }}"

    def get_dag_run_id(**kwargs):
        run_id = kwargs['dag_run'].run_id
        print(f"Generated run_id  : {run_id}")
        print(f"Timestamp  : {pendulum.now()}")
        return run_id

    def choose_engine(**kwargs):
        """
        Choose engine based on engine_type from configuration
        Returns task_id of the engine to execute
        """
        dag_run = kwargs['dag_run']
        conf = dag_run.conf if dag_run.conf else {}
        engine_type = conf.get('engine_type', 'spark')  # Default to spark
        
        print(f"Run Now: Engine type detected: {engine_type}")
        print(f"Run Now: Full config: {conf}")
        
        if isinstance(engine_type, str) and engine_type.lower() == 'dlt':
            selected_task = 'run_now_dlt_task'
            print(f" DECISION: DLT Engine selected -> {selected_task}")
            print(" Will execute: DLT pipeline with dlt_runner.py")
            return selected_task  
        else:
            selected_task = 'run_now_job_task'
            print(f" DECISION: Spark Engine selected -> {selected_task}")
            print(" Will execute: Spark job with SparkSubmitOperator")
            return selected_task 

    #  Get run ID 
    get_run_id_task = PythonOperator(
        task_id="get_run_id",
        python_callable=get_dag_run_id,
        provide_context=True
    )

    #  Choose engine based on engine_type
    choose_engine_task = BranchPythonOperator(
        task_id='choose_engine',
        python_callable=choose_engine,
        provide_context=True
    )

    #  Spark execution 
    run_now_job_task = SparkSubmitOperator(
        task_id="run_now_job_task",
        conn_id='spark_default',
        application=get_conf("spark_path"),
        packages=get_conf("spark_packages"),
        name='my_spark_app',
        py_files=get_conf("helper_module", ""),
        application_args=[
            get_conf("job_id", ""),
            get_conf("user_id", ""),
            get_conf("schedule_id", ""),
            "{{ ti.xcom_pull(task_ids='get_run_id') }}",
            get_conf('execution_type', 'default')
        ]
    )

    run_now_dlt_task = BashOperator(
        task_id='run_now_dlt_task',
        bash_command=r"""
        set -euo pipefail
        echo " Starting DLT execution "
        echo "  - Job ID: {{ dag_run.conf.get('job_id', '') }}"
        echo "  - User ID: {{ dag_run.conf.get('user_id', '') }}"
        echo "  - Schedule ID: {{ dag_run.conf.get('schedule_id', '') }}"
        echo "  - Engine Type: {{ dag_run.conf.get('engine_type', 'dlt') }}"
        echo "  - Execution Type: {{ dag_run.conf.get('execution_type', 'code') }}"
        echo "  - Run ID: {{ ti.xcom_pull(task_ids='get_run_id') }}"
        echo "  - Environment: {{ dag_run.conf.get('environment', 'dev') }}"
        echo "  - Extra Packages: {{ dag_run.conf.get('pip_packages', '') }}"

        # Create directories in Airflow container (already mounted to host)
        mkdir -p /opt/airflow/dlt/dlt_data
        mkdir -p /opt/airflow/dlt/dlt_state/{{ dag_run.conf.get('schedule_id', 'default') }}

        ENVIRONMENT="{{ dag_run.conf.get('environment', 'dev') }}"
        SCHEDULE_ID="{{ dag_run.conf.get('schedule_id', 'default') }}"
        CURRENT_CONTAINER=$(hostname)
        EXTRA_PACKAGES="{{ dag_run.conf.get('pip_packages', '') }}"

        # KEY CHANGE: Use ONLY --volumes-from, NO explicit -v mounts
        # Set DLT_DATA_DIR to Airflow's path (which is already mounted to host)
        exec docker run --rm \
        --network=opendatapipeline_open-data-pipeline-cluster \
        --volumes-from "$CURRENT_CONTAINER" \
        -e DLT_DATA_DIR="/opt/airflow/dlt/dlt_state/$SCHEDULE_ID" \
        -e APP_ENVIRONMENT="$ENVIRONMENT" \
        -e PYTHONPATH="/app:/app/audit_tracker:/app/core:/opt/airflow/inbuilt_modules" \
        -e EXTRA_PACKAGES="$EXTRA_PACKAGES" \
        open-data-pipeline-dlt-task-image \
        /bin/bash -lc '
            set -euo pipefail
            echo "DLT_DATA_DIR: $DLT_DATA_DIR"
            
            if [ -n "${EXTRA_PACKAGES:-}" ]; then
            echo "Installing packages: $EXTRA_PACKAGES"
            echo "Installing extra packages: BEGIN"
            mapfile -t pkgs < <(printf "%s\n" "$EXTRA_PACKAGES" | tr " " "\n")
            python -m pip install --no-cache-dir --upgrade "${pkgs[@]}"
            echo "Installing extra packages: DONE"
            else
            echo "No extra packages requested."
            fi

            python dlt_runner.py \
            "{{ dag_run.conf.get('job_id', '') }}" \
            "{{ dag_run.conf.get('user_id', '') }}" \
            "{{ dag_run.conf.get('schedule_id', '') }}" \
            "{{ ti.xcom_pull(task_ids='get_run_id') }}" \
            "{{ dag_run.conf.get('execution_type', 'code') }}" \
            "dts"
        '
        """,
    )

    # Define task dependencies
    get_run_id_task >> choose_engine_task
    choose_engine_task >> run_now_job_task
    choose_engine_task >> run_now_dlt_task
