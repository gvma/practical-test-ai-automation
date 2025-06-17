"""create ticket_history table

Revision ID: e058553d9a1e
Revises: 900560df6097
Create Date: 2025-06-16 09:34:18.562302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f16666401f59'
down_revision: Union[str, None] = '900560df6097'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('ticket_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('change_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),  # type: ignore
        sa.PrimaryKeyConstraint('id')
    )

    op.add_column('ticket_history',
        sa.Column('priority', sa.Enum(name='priority_enum', create_type=False), nullable=False)
    )

    op.add_column('ticket_history',
        sa.Column('customer_tier', sa.Enum(name='customer_tier_enum', create_type=False), nullable=False)
    )
    
    op.add_column('ticket_history',
        sa.Column('status', sa.Enum(name='ticket_status_enum', create_type=False), nullable=False)
    )

    op.alter_column('ticket', 'status',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('ticket_history')
    # ### end Alembic commands ###
