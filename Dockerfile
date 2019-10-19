FROM python:3.7-slim
MAINTAINER Zerthmonk
 
ENV PYTHONUBUFFERED=1
ENV PATH="/venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential libpq-dev python3-dev python3-psycopg2 && \
    rm -rf /var/lib/apt/lists/* 

COPY ./requirements.txt /requirements.txt
RUN python -m venv /venv && \
    python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN useradd skaben
USER skaben
