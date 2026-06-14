"""Alembic env. Безсхемный режим — сравнения автогенерации нет, миграции пишутся
вручную в alembic/versions/. SQLite + raw SQL.
"""
from __future__ import annotations
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

# Загрузить URL из api.config если возможно
try:
    from api.config import get_settings
    db_path = get_settings().db_path
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
except Exception:
    pass

target_metadata = None  # raw SQL миграции


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata,
                       literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
