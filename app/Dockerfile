FROM python:3.11

RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y ffmpeg curl

WORKDIR /app

# Копируем файлы в контейнер
COPY . /app

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Ollama CLI (если оно еще не установлено)
RUN curl -sSL https://ollama.com/download/ollama-linux-amd64 -o /usr/local/bin/ollama && \
    chmod +x /usr/local/bin/ollama && \
    pip install ollama

# Создаем папку для моделей (если её нет)
RUN mkdir -p /root/.ollama/models

ENTRYPOINT ["python", "main.py"]
