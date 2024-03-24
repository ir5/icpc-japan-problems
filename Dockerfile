FROM python:3.10.13 AS builder

WORKDIR /app

COPY requirements-full.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements-full.txt

EXPOSE 8000
COPY . .
CMD ["python3", "main.py"]
