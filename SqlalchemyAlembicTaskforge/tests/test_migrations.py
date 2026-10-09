import sqlite3
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory

from alembic import command

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def alembic_config() -> Config:
    return Config(PROJECT_ROOT / "alembic.ini")


def test_complete_migration_chain_and_downgrade(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_path = tmp_path / "migrations.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    configuration = alembic_config()

    command.upgrade(configuration, "0005_seed_tags")
    with sqlite3.connect(database_path) as connection:
        tag_names = {row[0] for row in connection.execute("SELECT name FROM tags")}
        cursor = connection.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            ("remi_keys", "remi@cadence.example"),
        )
        user_id = cursor.lastrowid
        task_cursor = connection.execute(
            "INSERT INTO tasks (title, status, priority, owner_id) VALUES (?, ?, ?, ?)",
            ("Sketch the piano coda", "todo", 5, user_id),
        )
        task_id = task_cursor.lastrowid
        tagged_task_id = connection.execute(
            "INSERT INTO tasks (title, status, priority, owner_id) VALUES (?, ?, ?, ?)",
            ("Notate the violin motif", "todo", 3, user_id),
        ).lastrowid
        composition_id = connection.execute(
            "SELECT id FROM tags WHERE name = ?", ("composition",)
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)",
            (tagged_task_id, composition_id),
        )

    assert tag_names == {"composition", "rehearsal", "guitar", "keyboards", "recording"}

    command.upgrade(configuration, "head")
    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        columns = {row[1] for row in connection.execute("PRAGMA table_info(tasks)")}
        indexes = {row[1] for row in connection.execute("PRAGMA index_list(tasks)")}
        assigned_task = connection.execute(
            "SELECT task_id FROM task_tags WHERE task_id = ?",
            (task_id,),
        ).fetchone()

    assert "comments" in tables
    assert "due_date" in columns
    assert "ix_tasks_status" in indexes
    assert assigned_task == (task_id,)

    command.downgrade(configuration, "-1")
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT task_id FROM task_tags").fetchall() == [(tagged_task_id,)]

    command.upgrade(configuration, "head")
    revisions = list(ScriptDirectory.from_config(configuration).walk_revisions())
    assert len(revisions) == 6

    command.downgrade(configuration, "base")
    with sqlite3.connect(database_path) as connection:
        remaining = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            if not row[0].startswith("sqlite_")
        }
    assert remaining <= {"alembic_version"}
    command.upgrade(configuration, "head")
    command.check(configuration)
