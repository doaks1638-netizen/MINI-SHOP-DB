#!/bin/bash
set -e  # любая ошибка → скрипт падает немедленно

# Укажи правильный относительный путь к папке versions (например, alembic/versions)
VERSIONS_DIR="alembic/versions"

echo "Checking migrations..."

# Проверяем: если директория НЕ существует ИЛИ она пустая
if [ ! -d "$VERSIONS_DIR" ] || [ -z "$(ls -A "$VERSIONS_DIR" 2>/dev/null)" ]; then
    echo "No migrations found. Generating final revision..."
    uv run alembic revision --autogenerate -m 'final_revision'
else
    echo "Migrations already exist. Skipping autogenerate."
fi

echo "Applying migrations..."
uv run alembic upgrade head

echo "Done."

exec "$@"  # передать управление команде из CMD