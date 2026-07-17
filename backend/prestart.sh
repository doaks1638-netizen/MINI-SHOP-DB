#!/bin/bash
set -e  # любая ошибка → скрипт падает немедленно

echo "Applying migrations..."
uv run alembic upgrade head

echo "Done."

exec "$@"  # передать управление команде из CMD