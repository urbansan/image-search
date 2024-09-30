FROM python:3.11-slim

RUN pip install poetry

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .
COPY README.md .

RUN poetry install --without dev


EXPOSE 8000