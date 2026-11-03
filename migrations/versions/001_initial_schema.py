"""Initial Enterprise Schema Baseline

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-02 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Baseline schema is provisioned via sql/schema.sql and SQLAlchemy ORM metadata
    pass

def downgrade() -> None:
    pass
