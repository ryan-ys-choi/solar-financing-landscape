from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='solar_pipeline',
    default_args=default_args,
    description='Collect and load solar financial data',
    schedule_interval='@weekly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['solar'],
) as dag:

    collect = BashOperator(
        task_id='collect_data',
        bash_command='cd /opt/airflow && python scripts/collect.py',
    )

    init_schema = BashOperator(
        task_id='init_schema',
        bash_command='cd /opt/airflow && python scripts/init_schema.py',
    )

    load = BashOperator(
        task_id='load_data',
        bash_command='cd /opt/airflow && python scripts/load.py',
    )

    collect >> init_schema >> load
