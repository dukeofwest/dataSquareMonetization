FROM python:3.7-buster

ENV PYTHONUNBUFFERED=1

WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .

ENTRYPOINT /bin/bash
