FROM python:3.9-slim

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN python -m pip install -r requirements.txt

COPY bot.py /app

CMD ["python", "bot.py"]
