FROM python:3.10 as base
 
ENV PYTHONUBUFFERED=1 \
    VIRTUAL_ENV=/venv

RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-psycopg2 curl && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip


FROM base as builder

ENV PROJECT_ROOT=/opt/app/skaben
WORKDIR ${PROJECT_ROOT}
ENV PYTHONPATH="${PYTHONPATH}:${PROJECT_ROOT}"
COPY ./requirements.txt scripts/wait-for-it.sh /opt/app/
    
RUN python -m pip install --no-cache-dir -r /opt/app/requirements.txt
COPY entrypoint.sh /opt/app

RUN mkdir -p ${PROJECT_ROOT}/static && \
    chmod +x /opt/app/entrypoint.sh && \
    chmod +x /opt/app/wait-for-it.sh

EXPOSE 8000

CMD ["sh", "-c", "/opt/app/entrypoint.sh"]
