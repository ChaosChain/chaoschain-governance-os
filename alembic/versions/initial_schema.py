"""Initial schema

Revision ID: b6ae5da45e71
Revises: 
Create Date: 2024-12-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b6ae5da45e71'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ProposalStatus enum type
    op.execute("""
        CREATE TYPE proposal_status AS ENUM ('pending', 'simulated', 'verified');
    """)
    
    # Create SimulationStatus enum type
    op.execute("""
        CREATE TYPE simulation_status AS ENUM ('pending', 'running', 'completed', 'failed');
    """)
    
    # Create proposals table
    op.create_table(
        'proposals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('status', sa.Enum('pending', 'simulated', 'verified', name='proposal_status'), 
                  nullable=False, server_default='pending'),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('agent_sig', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proposals_id'), 'proposals', ['id'], unique=False)
    
    # Create simulation_runs table
    op.create_table(
        'simulation_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('proposal_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', name='simulation_status'), 
                  nullable=False, server_default='pending'),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_simulation_runs_id'), 'simulation_runs', ['id'], unique=False)
    
    # Create attestations table
    op.create_table(
        'attestations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('proposal_id', sa.Integer(), nullable=False),
        sa.Column('enclave_id', sa.String(length=255), nullable=False),
        sa.Column('payload_hash', sa.String(length=255), nullable=False),
        sa.Column('signature', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('proposal_id')
    )
    op.create_index(op.f('ix_attestations_id'), 'attestations', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_table('attestations')
    op.drop_table('simulation_runs')
    op.drop_table('proposals')
    
    # Drop enum types
    op.execute('DROP TYPE simulation_status;')
    op.execute('DROP TYPE proposal_status;') 