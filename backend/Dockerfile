FROM python:3.12.2-bookworm AS builder

WORKDIR /backend

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY backend/pyproject.toml backend/uv.lock ./

RUN uv sync --no-install-project

FROM python:3.12.2-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY .env /mini_shop_db/

WORKDIR /backend

COPY --from=builder /backend/.venv .venv 

COPY backend/ ./

ENTRYPOINT [ "./prestart.sh" ]

