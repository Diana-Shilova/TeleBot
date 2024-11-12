# Используем базовый образ с Python
FROM python:3.11

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y ffmpeg

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы в контейнер
COPY . /app

# Устанавливаем Python-пакеты
RUN pip install --no-cache-dir -r requirements.txt

# Указываем команду запуска
ENTRYPOINT ["python", "main.py"]
