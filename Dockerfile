FROM python:3.11.1-slim

WORKDIR /isocial

COPY poetry.lock pyproject.toml ./

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-root

COPY . .

EXPOSE 8000