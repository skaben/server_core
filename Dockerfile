FROM python:3.7-slim as base
 
ENV PYTHONUBUFFERED=1
ENV PATH="/venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential libpq-dev python3-dev python3-psycopg2 curl && \
    rm -rf /var/lib/apt/lists/* 

FROM base as builder

COPY ./requirements.txt ./docker_build/scripts/* /
    
RUN python -m venv /venv && \
    python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r /requirements.txt && \
    mkdir -p /skaben/static && \
    chmod +x /entrypoint*.sh && \
    chmod +x /wait-for-it.sh

WORKDIR /skaben
