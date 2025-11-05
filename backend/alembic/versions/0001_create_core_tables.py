"""create core tables

Revision ID: 0001_create_core_tables
Revises: 
Create Date: 2025-11-05 00:00:00

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_create_core_tables"
down_revision = None
branch_labels = None
depends_on = None

# Reuse this in both create_table and upgrade/downgrade hooks
INGESTION_STATUS = sa.Enum(
    "pending",
    "succeeded",
    "failed",
    name="ingestion_status",
    create_type=False,  # prevent implicit CREATE TYPE; we'll control it
)


def upgrade() -> None:
    bind = op.get_bind()

    # # Ensure enum exists (no-op if already created)
    # INGESTION_STATUS.create(bind, checkfirst=True)

    # documents table
    op.create_table(
        "documents",
        sa.Column("document_id", sa.String(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=False),
        sa.Column("owner", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_indexed", sa.DateTime(timezone=True), nullable=True),
        sa.Column("content_hash", sa.String(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("ingestion_status", sa.String(), nullable=False),
        # sa.Column(
        #     "ingestion_status",
        #     INGESTION_STATUS,
        #     nullable=False,
        #     server_default="pending",
        # ),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
    )

    # conversations table
    op.create_table(
        "conversations",
        sa.Column("conversation_id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=False),
    )

    # queries table
    op.create_table(
        "queries",
        sa.Column("query_id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("embedding_id", sa.String(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "conversation_id",
            sa.String(),
            sa.ForeignKey("conversations.conversation_id"),
            nullable=True,
        ),
    )

    # sections table
    op.create_table(
        "sections",
        sa.Column("section_id", sa.String(), primary_key=True),
        sa.Column(
            "document_id",
            sa.String(),
            sa.ForeignKey("documents.document_id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("char_offset_start", sa.Integer(), nullable=True),
        sa.Column("char_offset_end", sa.Integer(), nullable=True),
        sa.Column("embedding_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # responses table
    op.create_table(
        "responses",
        sa.Column("response_id", sa.String(), primary_key=True),
        sa.Column(
            "query_id",
            sa.String(),
            sa.ForeignKey("queries.query_id"),
            nullable=False,
        ),
        sa.Column("generated_text", sa.Text(), nullable=False),
        sa.Column("source_sections", sa.JSON(), nullable=False),
        sa.Column("confidence_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    bind = op.get_bind()

    op.drop_table("responses")
    op.drop_table("sections")
    op.drop_table("queries")
    op.drop_table("conversations")
    op.drop_table("documents")

    # Drop enum only if it exists and is unused
    INGESTION_STATUS.drop(bind, checkfirst=True)
