from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from clear_folder_dag.function.clear_folder import clear_folder
from install_models_dag.function.install_models import download_model

# Путь к папке для чистки
folder_path = "/opt/app/all_info_for_drive"

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

with DAG(
    dag_id="main_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
) as dag:

    # Оператор для скачивания моделей
    download_models_task = PythonOperator(
        task_id="download_models_task",
        python_callable=download_model,
        dag=dag,
        execution_timeout=timedelta(minutes=30)
    )

    # Оператор для очистки папки
    clear_folder_task = PythonOperator(
        task_id="clear_folder_task",
        python_callable=clear_folder,
        op_args=[folder_path]
    )

    # Зависимости задач
    download_models_task >> clear_folder_task
