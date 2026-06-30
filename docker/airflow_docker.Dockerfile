FROM apache/airflow:2.9.3-python3.8

# Copy the airflow directory with ownership set to airflow:root
COPY --chown=airflow:root /airflow /airflow_tmp
#COPY --chown=airflow:root /airflow/requirements.txt /airflow/requirements.txt
# Change the permissions to 770 (drwxrwx---)
USER root
RUN mkdir /airflow && \
    chown airflow:root /airflow

RUN chmod -R 770 /airflow_tmp

RUN chmod -R 770 /airflow
USER airflow
RUN  pip install --no-cache-dir -r /airflow_tmp/requirements.txt
