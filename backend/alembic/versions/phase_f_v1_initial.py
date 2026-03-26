"""
Add performance metrics table and extended publish fields to video jobs.

Revision ID: phase_f_v1
Revises: 
Create Date: 2026-03-26 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'phase_f_v1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Create performance_metrics table ──
    op.create_table(
        'performance_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('views', sa.Integer(), nullable=True),
        sa.Column('watch_time_seconds', sa.Integer(), nullable=True),
        sa.Column('ctr_estimate', sa.Float(), nullable=True),
        sa.Column('conversions', sa.Integer(), nullable=True),
        sa.Column('operator_rating', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='manual'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('operator_rating IS NULL OR (operator_rating >= 1 AND operator_rating <= 5)', name='ck_operator_rating_range'),
        sa.ForeignKeyConstraint(['job_id'], ['video_jobs.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_performance_metrics_job_id'), 'performance_metrics', ['job_id'], unique=False)

    # ── Add new columns to video_jobs ──
    op.add_column('video_jobs', sa.Column('operator_notes', sa.Text(), nullable=True))
    op.add_column('video_jobs', sa.Column('publish_outcome', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # ── Remove columns from video_jobs ──
    op.drop_column('video_jobs', 'publish_outcome')
    op.drop_column('video_jobs', 'operator_notes')

    # ── Drop performance_metrics table ──
    op.drop_index(op.f('ix_performance_metrics_job_id'), table_name='performance_metrics')
    op.drop_table('performance_metrics')
