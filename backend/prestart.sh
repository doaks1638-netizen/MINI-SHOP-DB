#!/bin/bash
set -e  # любая ошибка → скрипт падает немедленно
        # лучше явный крэш, чем работа в сломанном состоянии

echo "Applying migrations..."
uv run alembic revision --autogenerate -m 'final_revision'
uv run alembic upgrade head

echo "Done."

exec "$@"  # передать управление команде из CMD