FROM apache/airflow:2.5.0

USER root

# Установка необходимых пакетов
RUN mkdir -p /var/lib/apt/lists/partial && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    apt-get install -y libpq-dev && \
    apt-get clean

# Установка рабочей директории
WORKDIR /opt/airflow

# Копируем DAG файлы и скрипты функций
COPY . /opt/airflow/dags

# Копируем файл с зависимостями
COPY requirements.txt /opt/airflow/requirements.txt

# Переключаемся на пользователя airflow
USER airflow

# Установка Python-зависимостей
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Загружаем модели при сборке контейнера
RUN python /opt/airflow/dags/install_models_dag/function/install_models.py

# Инициализация базы данных Airflow
RUN airflow db init
