from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_seed_tags"
down_revision: str | None = "0004_comments"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TAG_NAMES = ("composition", "rehearsal", "guitar", "keyboards", "recording")


def tags_table() -> sa.TableClause:
    return sa.table(
        "tags",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String()),
    )


def upgrade() -> None:
    op.bulk_insert(tags_table(), [{"name": name} for name in TAG_NAMES])


def downgrade() -> None:
    table = tags_table()
    associations = sa.table(
        "task_tags",
        sa.column("task_id", sa.Integer()),
        sa.column("tag_id", sa.Integer()),
    )
    seeded_ids = sa.select(table.c.id).where(table.c.name.in_(TAG_NAMES))
    op.execute(associations.delete().where(associations.c.tag_id.in_(seeded_ids)))
    op.execute(table.delete().where(table.c.name.in_(TAG_NAMES)))
