from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_default_tag"
down_revision: str | None = "0005_seed_tags"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def migration_tables() -> tuple[sa.TableClause, sa.TableClause, sa.TableClause]:
    tags = sa.table("tags", sa.column("id", sa.Integer()), sa.column("name", sa.String()))
    tasks = sa.table("tasks", sa.column("id", sa.Integer()))
    task_tags = sa.table(
        "task_tags",
        sa.column("task_id", sa.Integer()),
        sa.column("tag_id", sa.Integer()),
    )
    return tags, tasks, task_tags


def upgrade() -> None:
    op.create_table(
        "composition_tag_backfill",
        sa.Column("task_id", sa.Integer(), primary_key=True),
        sa.Column("tag_id", sa.Integer(), nullable=False),
    )
    connection = op.get_bind()
    tags, tasks, task_tags = migration_tables()
    tag_id = connection.execute(
        sa.select(tags.c.id).where(tags.c.name == "composition")
    ).scalar_one_or_none()
    if tag_id is None:
        return
    untagged_task_ids = list(
        connection.execute(
            sa.select(tasks.c.id)
            .outerjoin(task_tags, tasks.c.id == task_tags.c.task_id)
            .where(task_tags.c.task_id.is_(None))
        ).scalars()
    )
    if untagged_task_ids:
        assignments = [{"task_id": task_id, "tag_id": tag_id} for task_id in untagged_task_ids]
        connection.execute(
            task_tags.insert(),
            assignments,
        )
        backfill = sa.table(
            "composition_tag_backfill",
            sa.column("task_id", sa.Integer()),
            sa.column("tag_id", sa.Integer()),
        )
        connection.execute(backfill.insert(), assignments)


def downgrade() -> None:
    connection = op.get_bind()
    _, _, task_tags = migration_tables()
    backfill = sa.table(
        "composition_tag_backfill",
        sa.column("task_id", sa.Integer()),
        sa.column("tag_id", sa.Integer()),
    )
    connection.execute(
        task_tags.delete().where(
            sa.exists(
                sa.select(backfill.c.task_id).where(
                    backfill.c.task_id == task_tags.c.task_id,
                    backfill.c.tag_id == task_tags.c.tag_id,
                )
            )
        )
    )
    op.drop_table("composition_tag_backfill")
