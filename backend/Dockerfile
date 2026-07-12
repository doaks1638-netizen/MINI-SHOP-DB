FROM python:3.12.2-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY .env /mini_shop_db/
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /mini_shop_db

COPY backend/pyproject.toml backend/uv.lock ./

RUN uv sync --frozen --no-cache --no-dev

COPY backend/ /mini_shop_db/

ENTRYPOINT [ "./prestart.sh" ]

# no CMD where. go to docker-compose.yaml -> web -> command: gunicorn...