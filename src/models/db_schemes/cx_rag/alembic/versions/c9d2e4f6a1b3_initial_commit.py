"""initial commit

Revision ID: c9d2e4f6a1b3
Revises:
Create Date: 2026-10-03 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c9d2e4f6a1b3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('assets',
    sa.Column('asset_id', sa.Integer(), nullable=False),
    sa.Column('asset_uuid', sa.Uuid(), nullable=False),
    sa.Column('asset_type', sa.Unicode(length=50), nullable=False),
    sa.Column('asset_name', sa.Unicode(length=255), nullable=False),
    sa.Column('asset_size', sa.Integer(), nullable=False),
    sa.Column('asset_config', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('asset_id')
    )
    op.create_index('ix_asset_type', 'assets', ['asset_type'], unique=False)
    op.create_index(op.f('ix_assets_asset_id'), 'assets', ['asset_id'], unique=False)
    op.create_index(op.f('ix_assets_asset_uuid'), 'assets', ['asset_uuid'], unique=True)
    op.create_table('chunks',
    sa.Column('chunk_id', sa.Integer(), nullable=False),
    sa.Column('chunk_uuid', sa.Uuid(), nullable=False),
    sa.Column('chunk_text', sa.UnicodeText(), nullable=False),
    sa.Column('chunk_metadata', sa.JSON(), nullable=True),
    sa.Column('chunk_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('chunk_asset_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['chunk_asset_id'], ['assets.asset_id'], ),
    sa.PrimaryKeyConstraint('chunk_id')
    )
    op.create_index('ix_chunk_asset_id', 'chunks', ['chunk_asset_id'], unique=False)
    op.create_index(op.f('ix_chunks_chunk_id'), 'chunks', ['chunk_id'], unique=False)
    op.create_index(op.f('ix_chunks_chunk_uuid'), 'chunks', ['chunk_uuid'], unique=True)
    op.create_table('messages',
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('message_conversation_id', sa.Unicode(length=64), nullable=False),
    sa.Column('message_role', sa.Unicode(length=20), nullable=False),
    sa.Column('message_content', sa.UnicodeText(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('message_id')
    )
    op.create_index('ix_message_conversation_id', 'messages', ['message_conversation_id'], unique=False)
    op.create_index(op.f('ix_messages_message_id'), 'messages', ['message_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_messages_message_id'), table_name='messages')
    op.drop_index('ix_message_conversation_id', table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_chunks_chunk_uuid'), table_name='chunks')
    op.drop_index(op.f('ix_chunks_chunk_id'), table_name='chunks')
    op.drop_index('ix_chunk_asset_id', table_name='chunks')
    op.drop_table('chunks')
    op.drop_index(op.f('ix_assets_asset_uuid'), table_name='assets')
    op.drop_index(op.f('ix_assets_asset_id'), table_name='assets')
    op.drop_index('ix_asset_type', table_name='assets')
    op.drop_table('assets')
