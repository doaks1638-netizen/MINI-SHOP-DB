FROM python:3.12.2-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /mini_shop_db

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache

COPY . /mini_shop_db/

ENTRYPOINT [ "./prestart.sh" ]

# no CMD where. go to docker-compose.yaml -> web -> command: gunicorn...