in rest-trigger give dag file path of local machine



	dag_file_path = f'/home/praveen/my_airflow/dags/{job_id}.py'



1. Updated config.py file
     - localhost URL is updated


2.updated flask_api_create_del_log.py 
     - removed previous dag_log function and 

     - added fetch_log function to fetch log for given job_id
             
           - input - param  : job_id 