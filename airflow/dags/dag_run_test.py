from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 7, 8),
}

with DAG('dbt_test_movies',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    test_movie_id = BashOperator(
        task_id='test_movie_id_not_null',
        bash_command="cd /mnt/dbt/cinema/ && dbt test --select test_movie_id_is_not_null"
    )
