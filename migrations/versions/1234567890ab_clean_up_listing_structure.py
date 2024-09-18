"""Clean up listing table structure

Revision ID: 1234567890ab
Revises: 98390ec7fbd3
Create Date: 2024-09-16 00:00:00

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '1234567890ab'
down_revision = '98390ec7fbd3'
branch_labels = None
depends_on = None


def upgrade():
    # Get the bind object
    bind = op.get_bind()

    # Create an inspector
    inspector = inspect(bind)

    # Check if the 'listing' table exists
    if inspector.has_table('listing'):
        # Drop the 'location' column
        if 'location' in inspector.get_columns('listing'):
            with op.batch_alter_table('listing', schema=None) as batch_op:
                batch_op.drop_column('location')
            print("'location' column dropped from 'listing' table.")

        # Drop the 'city' column
        if 'city' in inspector.get_columns('listing'):
            with op.batch_alter_table('listing', schema=None) as batch_op:
                batch_op.drop_column('city')
            print("'city' column dropped from 'listing' table.")
    else:
        print("'listing' table does not exist.")


def downgrade():
    # This migration doesn't have a direct downgrade operation
    pass
