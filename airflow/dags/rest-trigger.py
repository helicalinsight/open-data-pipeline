
import uuid
import textwrap
from datetime import datetime, timedelta
from airflow import DAG  # Importing DAG here
from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
import pendulum
from dotenv import load_dotenv
import os
load_dotenv()

DAGS_PATH = os.getenv('AIRFLOW_HOME')
if not DAGS_PATH:
        raise EnvironmentError("The AIRFLOW_HOME environment variable is not set.")

def generate_dag_content(
        job_id, schedule_interval, user_id, job_name, advanced_scheduling, schedule_id, spark_path, spark_packages,
        local, schedule_name, executionType, spark_conf=None, notification={}, helper_module=None,
        engine_type='spark', input_run_id=None, generated_cron_expression=None, pip_packages="", service_type="dts"
    ):
    """
    Generate DAG content for both Spark and DLT engines
    Uses simple BashOperator for DLT 
    
    Now uses pre-generated cron expression from airflow_service instead of generating here
    For DLT: installs EXTRA_PACKAGES inside the task container before running dlt_runner.py.
    """

    # Use pre-generated cron expression if available, otherwise fallback to basic schedule
    if generated_cron_expression:
        schedule_interval = generated_cron_expression
    else:
        # Fallback to basic schedule interval
        schedule_interval = f'@{schedule_interval}'

    now = datetime.now()
    new_time = now + timedelta(minutes=1)
    start_date = new_time.date()
    start_time = new_time.time()
    end_date = None
    end_time = None
    timezone = "UTC"
    end_datetime = None
    end_after_executions = None

    # Handle advanced scheduling if provided (for date/time calculations only)
    if advanced_scheduling:
        end_after_executions = advanced_scheduling.get("EndAfterExecutions")
        timezone = advanced_scheduling.get("timeZone", "UTC")
        start_date = datetime.strptime(advanced_scheduling["StartDate"], "%Y-%m-%d")
        start_time = datetime.strptime(advanced_scheduling["StartTime"], "%H:%M:%S").time()

        if advanced_scheduling.get("EndDate"):
            end_date = datetime.strptime(advanced_scheduling["EndDate"], "%Y-%m-%d")
            end_time = datetime.strptime(advanced_scheduling["EndTime"], "%H:%M:%S").time()

        if advanced_scheduling.get("ends") == "after":
            end_after_executions = advanced_scheduling.get("EndAfterExecutions")

    # Calculate the start datetime
    start_datetime = datetime.combine(start_date, start_time).isoformat()

    # Calculate the end datetime if provided
    if end_date and end_time:
        end_datetime = datetime.combine(end_date, end_time).isoformat()

    # If the schedule should end after a certain number of executions, adjust the max_active_runs
    default_args = {}
    if end_after_executions:
        default_args["max_active_runs"] = end_after_executions

    if input_run_id is not None:
        run_id_code = input_run_id
    else:
        run_id_code = "{{{{ ti.xcom_pull(task_ids='get_run_id') }}}}"
    # Generate engine-specific task content
    if engine_type == 'dlt':
        # Normalize Jinja braces ONLY for DLT so the generated DAG contains {{ ... }} not {{{{ ... }}}}
        dlt_run_id_code = run_id_code
        if isinstance(dlt_run_id_code, str):
            dlt_run_id_code = dlt_run_id_code.replace("{{{{", "{{").replace("}}}}", "}}")

        # DLT: pass in EXTRA_PACKAGES captured at schedule creation time
        # and install them in the task container before running dlt_runner.py
        task_content = f"""
    run_dlt_task = BashOperator(
        task_id='run_dlt_task',
        bash_command=r\"\"\"
set -euo pipefail

echo "Starting DLT execution (scheduled)"
echo "  - Job ID: {job_id}"
echo "  - User ID: {user_id}"
echo "  - Schedule ID: {schedule_id}"
echo "  - Engine Type: dlt"
echo "  - Execution Type: {executionType}"
echo "  - Run ID: {dlt_run_id_code}"
echo "  - Extra Packages: {pip_packages if pip_packages else 'None'}"


# Create directories in Airflow container (already mounted to host)
mkdir -p /opt/airflow/dlt/dlt_data
mkdir -p /opt/airflow/dlt/dlt_state/{schedule_id}

ENVIRONMENT="${{APP_ENVIRONMENT:-dev}}"
CURRENT_CONTAINER=$(hostname)
EXTRA_PACKAGES="{pip_packages if pip_packages else ''}"

echo "Airflow container: $CURRENT_CONTAINER"
echo "Schedule ID: {schedule_id}"

# Use ONLY --volumes-from, set DLT to write to Airflow paths
exec docker run --rm \\
  --network=opendatapipeline_open-data-pipeline-cluster \\
  --volumes-from "$CURRENT_CONTAINER" \\
  -e DLT_DATA_DIR="/opt/airflow/dlt/dlt_state/{schedule_id}" \\
  -e APP_ENVIRONMENT="$ENVIRONMENT" \\
  -e PYTHONPATH="/app:/app/audit_tracker:/app/core:/opt/airflow/inbuilt_modules" \\
  -e EXTRA_PACKAGES="$EXTRA_PACKAGES" \\
  open-data-pipeline-dlt-task-image \\
  /bin/bash -lc '
    set -euo pipefail
    
    if [ -n "${{EXTRA_PACKAGES:-}}" ]; then
      echo "Installing packages: $EXTRA_PACKAGES"
      mapfile -t pkgs < <(printf "%s\\n" "$EXTRA_PACKAGES" | tr " " "\\n")
      python -m pip install --no-cache-dir --upgrade "${{pkgs[@]}}"
      echo "Installing extra packages: DONE"
    else
      echo "No extra packages requested."
    fi

    python dlt_runner.py \\
      "{job_id}" \\
      "{user_id}" \\
      "{schedule_id}" \\
      "{dlt_run_id_code}" \\
      "{executionType}" \\
      "{service_type}"
  '
\"\"\",\n
        on_failure_callback=failure_callback,
        on_success_callback=success_callback,
    )
    get_run_id_task >> run_dlt_task"""

        # Imports for DLT
        imports_section = """from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from notification.notifier import Notifier
import pendulum"""

    else:
        task_content = f"""
    submit_spark_app = SparkSubmitOperator(
        task_id='submit_spark_app',
        conn_id='spark_default',
        application=f'{spark_path}', packages=f'{spark_packages}',
        name='my_spark_app',
        py_files=f'{helper_module}',
        on_failure_callback=failure_callback,
        on_success_callback=success_callback,
        application_args=[f"{job_id}", f"{user_id}", f"{schedule_id}", f"{run_id_code}", f"{executionType}"]
    )
    get_run_id_task >> submit_spark_app"""

        imports_section = """from airflow.decorators import dag, task
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from notification.notifier import Notifier
import pendulum"""

    return textwrap.dedent(f"""
{imports_section}
end_date='{end_date}'
end_datetime='{end_datetime}'
notification={notification}
engine_type='{engine_type}'
if end_date =='None':
    end_date=None

timezone='{timezone}'
def get_dag_run_id(**kwargs):
    return kwargs['dag_run'].run_id

def failure_callback(context):
    if notification.get("active"):
        notificaiton_obj = Notifier.create_object(notification=notification)
        context["notify_details"] = notification.get("details")
        context["schedule_id"] = '{schedule_id}'
        notificaiton_obj.notifier(**context)

def success_callback(context):
    if notification.get("active"):
        notificaiton_obj = Notifier.create_object(notification=notification)
        context["notify_details"] = notification.get("details")
        context["schedule_id"] = '{schedule_id}'
        notificaiton_obj.notifier(**context)

@dag(
    dag_id='{schedule_id}',
    default_args={{   
            'owner': 'airflow',
            'start_date' : pendulum.parse('{start_datetime}', tz='{timezone}'),
            'end_date' : pendulum.parse(end_datetime, tz=timezone) if end_date else None,
        }},
    schedule_interval='{schedule_interval}',
    catchup=False,
    is_paused_upon_creation=False,
    tags=[f'user_id:{user_id}', f'job_name:{job_name}', f'local:{local}', f'schedule_name:{schedule_name}', f'engine_type:{engine_type}', f'service_type:{service_type}'],
)
def autogenerated_dag():
    get_run_id_task = PythonOperator(
        task_id='get_run_id',
        python_callable=get_dag_run_id,
        provide_context=True
    )
{task_content}

dag_instance = autogenerated_dag()
    """).lstrip()

def run_this_func(ti, **context):
    job_id = context['dag_run'].conf['job_id']
    schedule_interval = context['dag_run'].conf['schedule_interval']
    user_id = context['dag_run'].conf['user_id']
    job_name = context['dag_run'].conf['job_name']
    advanced_scheduling = context["dag_run"].conf.get('advanced_scheduling')
    schedule_id = context["dag_run"].conf.get('schedule_id')
    spark_path = context["dag_run"].conf.get('spark_path')
    spark_packages = context["dag_run"].conf.get('spark_packages')
    local = context["dag_run"].conf.get('local')
    schedule_name = context["dag_run"].conf.get('schedule_name')
    executionType = context["dag_run"].conf.get('executionType')
    spark_conf = context["dag_run"].conf.get('spark_conf')
    notification = context["dag_run"].conf.get('notification')
    helper_module = context["dag_run"].conf.get('helper_module')
    input_run_id = context['dag_run'].conf.get('run_id', None)
    engine_type = context["dag_run"].conf.get('engine_type', 'spark')  # Default to spark
    generated_cron_expression = context["dag_run"].conf.get('generated_cron_expression', None)
    service_type = context["dag_run"].conf.get('service_type', 'dts')  # Default to 'dts' (data transformation service) for regular DAGs

    # Extra pip packages to install for DLT scheduled jobs
    pip_packages = context["dag_run"].conf.get('pip_packages', "")

    print("JOB NAME IS:", job_name)
    print(f"ENGINE TYPE IS: {engine_type}")

    dag_content = generate_dag_content(
        job_id, schedule_interval, user_id, job_name,
        advanced_scheduling, schedule_id, spark_path, spark_packages,
        local, schedule_name, executionType, spark_conf,
        notification, helper_module, engine_type, input_run_id,
        generated_cron_expression, pip_packages=pip_packages, service_type=service_type
    )

    dag_file_path = f'{DAGS_PATH}/dags/{schedule_id}.py'
    with open(dag_file_path, 'w') as file:
        file.write(dag_content)
    print(f"DAG file created at {dag_file_path}")
    print(f"DAG will execute using {engine_type} engine")

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now(),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dagss = DAG(
    dag_id='rest-trigger',
    default_args=default_args,
    schedule_interval=None,
    tags=["airflow"]
)

t1 = PythonOperator(
    task_id="main_etl",
    python_callable=run_this_func,
    dag=dagss
)

t1
