"""create ticket table

Revision ID: 900560df6097
Revises: 
Create Date: 2025-06-15 19:34:23.080398

"""
from typing import Sequence, Union

from sqlalchemy.dialects.postgresql import ENUM

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '900560df6097'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


priority_enum = ENUM('LOW', 'MEDIUM', 'HIGH', name='priority_enum', create_type=False)
customer_tier_enum = ENUM('BRONZE', 'SILVER', 'GOLD', 'PLATINUM', name='customer_tier_enum', create_type=False)
ticket_status_enum = ENUM('OPEN', 'ONGOING', 'CLOSED', name='ticket_status_enum', create_type=False)
escalation_level_enum = ENUM('ALERT', 'BREACH', name='escalation_level_enum', create_type=False)

def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE TYPE priority_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH')"
    )
    op.execute(
        "CREATE TYPE customer_tier_enum AS ENUM ('BRONZE', 'SILVER', 'GOLD', 'PLATINUM')"
    )
    
    op.execute(
        "CREATE TYPE ticket_status_enum AS ENUM ('OPEN', 'ONGOING', 'CLOSED')"
    )
    
    op.execute(
        "CREATE TYPE escalation_level_enum AS ENUM ('ALERT', 'BREACH')"
    )

    op.create_table('ticket',
        sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
        sa.Column('priority', priority_enum, nullable=False), # type: ignore
        sa.Column('customer_tier', customer_tier_enum, nullable=False), # type: ignore
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', ticket_status_enum, nullable=False), # type: ignore
        sa.Column('escalation_level', escalation_level_enum, nullable=True), # type: ignore
        sa.PrimaryKeyConstraint('id')
    )

    op.add_column('ticket', sa.Column('resolved_at', sa.DateTime(), nullable=True))
    op.add_column('ticket', sa.Column('response_sla_deadline', sa.DateTime(), nullable=False))
    op.add_column('ticket', sa.Column('resolution_sla_deadline', sa.DateTime(), nullable=False))
    op.create_index('ix_ticket_customer_tier', 'ticket', ['customer_tier'], unique=False)
    op.create_index('ix_ticket_priority', 'ticket', ['priority'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_ticket_priority', table_name='ticket')
    op.drop_index('ix_ticket_customer_tier', table_name='ticket')
    op.drop_table('ticket')
    
    op.execute("DROP TYPE IF EXISTS priority_enum")
    op.execute("DROP TYPE IF EXISTS customer_tier_enum")
    op.execute("DROP TYPE IF EXISTS ticket_status_enum")
    op.execute("DROP TYPE IF EXISTS escalation_level_enum")
    # ### end Alembic commands ###
