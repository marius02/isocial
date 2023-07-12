FROM python:3.11.1-slim

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN pip3 install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-root

COPY ./app .

EXPOSE 8000