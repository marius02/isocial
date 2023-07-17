FROM python:3.11.1-slim

WORKDIR /

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY ./app .


EXPOSE 8000