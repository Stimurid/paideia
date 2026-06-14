"""baseline — текущая схема Paideia из db/schema.sql

Revision ID: 0001
Revises:
Create Date: 2026-06-14
"""
from pathlib import Path
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Прогон schema.sql на чистой/существующей БД. IF NOT EXISTS делает
    миграцию идемпотентной — можно применять на live-БД без дропа."""
    schema_path = Path(__file__).resolve().parent.parent.parent / "db" / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    conn = op.get_bind()
    # Прогоняем как один скрипт. SQLite поддерживает.
    for statement in sql.split(";"):
        s = statement.strip()
        if s:
            conn.exec_driver_sql(s)


def downgrade() -> None:
    # Откат baseline невозможен без ручного восстановления из бэкапа.
    raise NotImplementedError("baseline rollback не поддерживается")
