"""create users and notes

Revision ID: cd43affc3138
Revises: 
Create Date: 2026-10-23 17:23:12.014456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'cd43affc3138'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('notes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.Text()), server_default=sa.text("'{}'"), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notes_created_at'), 'notes', ['created_at'], unique=False)
    op.create_index('ix_notes_tags', 'notes', ['tags'], unique=False, postgresql_using='gin')
    op.create_index(op.f('ix_notes_user_id'), 'notes', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notes_user_id'), table_name='notes')
    op.drop_index('ix_notes_tags', table_name='notes', postgresql_using='gin')
    op.drop_index(op.f('ix_notes_created_at'), table_name='notes')
    op.drop_table('notes')
    op.drop_table('users')
