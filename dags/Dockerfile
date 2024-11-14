FROM apache/airflow:2.5.0

USER root

RUN mkdir -p /var/lib/apt/lists/partial && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    apt-get install -y libpq-dev curl && \
    apt-get clean

WORKDIR /opt/airflow

COPY . /opt/airflow/dags
COPY requirements.txt /opt/airflow/requirements.txt

USER airflow

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Устанавливаем Ollama CLI
USER root
RUN curl -sSL https://ollama.com/download/ollama-linux-amd64 -o /usr/local/bin/ollama && \
    chmod +x /usr/local/bin/ollama && \
    pip install ollama

# Создаем папку для моделей внутри контейнера
RUN mkdir -p /root/.ollama/models

USER airflow
RUN airflow db init

WORKDIR /opt/airflow
