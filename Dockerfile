# AFM — optional Docker deployment path.
#
# render.yaml uses Render's native Python runtime by default (simpler,
# fewer moving parts). If you'd rather deploy as a container, switch the
# `afm-api` / `afm-worker` service blocks in render.yaml to:
#
#   runtime: docker
#   dockerfilePath: ./Dockerfile
#   dockerCommand: <see CMD overrides below>
#
# Docker-based Render services' support for preDeployCommand is less
# battle-tested than for native-runtime services, so migrations run from
# entrypoint.sh here instead — self-contained regardless of that.

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# build-essential: needed for source builds if a wheel is ever missing for
# the target platform (asyncpg/bcrypt/cryptography normally ship wheels,
# but this keeps the image resilient to that not being true on some arch).
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN useradd --create-home afm
USER afm

ENTRYPOINT ["/entrypoint.sh"]

# Default: run the API, listening on Render's dynamic $PORT. Override
# dockerCommand in render.yaml for the worker service, e.g.:
#   sh -c "python -m event_bus.worker"
CMD ["sh", "-c", "uvicorn api_gateway.main:app --host 0.0.0.0 --port ${PORT:-10000} --proxy-headers --forwarded-allow-ips=*"]
