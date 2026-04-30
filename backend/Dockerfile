# syntax=docker/dockerfile:1.7
# Backend SfM (development target).
# Pipeline Structure from Motion + API FastAPI sobre Python 3.12.

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependencias del sistema requeridas por opencv-contrib-python.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

FROM base AS dev
COPY requirements.txt pyproject.toml ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["sh", "-c", "uvicorn sfm_pipeline.api.server:app --host ${BACKEND_HOST:-0.0.0.0} --port ${BACKEND_INTERNAL_PORT:-8000} --reload"]
