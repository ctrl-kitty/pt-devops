# Используем базовый образ с поддержкой Python
FROM python:3.9-slim

# Установка зависимостей бота
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# Копирование файлов бота в образ
COPY bot.py /app

# Установка переменной окружения для токена бота
ENV BOT_TOKEN=${TOKEN}

# Команда для запуска бота
CMD ["python", "bot.py"]