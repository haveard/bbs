# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Install system packages we may need to build bcrypt (libffi, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create runtime user and data dir
RUN useradd -m bbs && \
    mkdir -p /app/data && \
    chown -R bbs:bbs /app

# Copy source
COPY bbs_server.py /app/bbs_server.py
COPY main.py /app/main.py

# Drop root
USER bbs

# Env vars
ENV BBS_PORT=2323
ENV BBS_DB_PATH=/app/data/bbs.sqlite3
ENV PYTHONUNBUFFERED=1

# Expose telnet-ish port
EXPOSE 2323/tcp

# Run the server using main.py entry point
CMD ["python", "/app/main.py"]