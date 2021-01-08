FROM python:3.8

WORKDIR /code
COPY requirements.txt .
COPY scripts ./scripts

RUN pip install -r requirements.txt