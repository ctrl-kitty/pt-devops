# Используем базовый образ с поддержкой Python
FROM python:3.9-slim

# Установка зависимостей бота
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN python -m pip install -r requirements.txt

# Копирование файлов бота в образ
COPY bot.py /app

# Установка переменной окружения для токена бота
ENV BOT_TOKEN=${TOKEN}
ENV RM_HOST=${RM_HOST}
ENV RM_PORT=${RM_PORT}
ENV RM_PASSWORD=${RM_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_NAME=${DB_NAME}
# Команда для запуска бота
CMD ["python", "bot.py"]
