"""make email unique

Revision ID: af796243ef56
Revises: b81d063ed2da
Create Date: 2024-11-10 17:38:36.226097

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'af796243ef56'
down_revision: Union[str, None] = 'b81d063ed2da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch operations for SQLite
    with op.batch_alter_table('users') as batch_op:
        batch_op.create_unique_constraint('uq_users_email', ['email'])


def downgrade() -> None:
    # Use batch operations for SQLite
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('uq_users_email', type_='unique')
