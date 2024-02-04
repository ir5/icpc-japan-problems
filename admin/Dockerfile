FROM python:3.10.13 AS builder

WORKDIR /admin

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install psycopg==3.1.17

COPY ./admin/. .
COPY ./.env .
