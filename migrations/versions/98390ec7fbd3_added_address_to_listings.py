"""added address to listings

Revision ID: 98390ec7fbd3
Revises: 6aaa7a910168
Create Date: 2024-09-15 20:10:22.157580

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '98390ec7fbd3'
down_revision = '6aaa7a910168'
branch_labels = None
depends_on = None


def upgrade():
    # Get the bind object
    bind = op.get_bind()

    # Create an inspector
    inspector = inspect(bind)

    # Check if the 'listing' table exists
    if inspector.has_table('listing'):
        # Check if the 'address' column already exists
        if 'address' not in inspector.get_columns('listing'):
            # Add the 'address' column if it doesn't exist
            with op.batch_alter_table('listing', schema=None) as batch_op:
                batch_op.add_column(sa.Column('address', sa.String(length=100), nullable=False))
            print("Added 'address' column to 'listing' table.")
        else:
            print("'address' column already exists in 'listing' table.")
    else:
        print("'listing' table does not exist.")


def downgrade():
    # Get the bind object
    bind = op.get_bind()

    # Create an inspector
    inspector = inspect(bind)

    # Check if the 'listing' table exists
    if inspector.has_table('listing'):
        # Drop the 'address' column if it exists
        if 'address' in inspector.get_columns('listing'):
            with op.batch_alter_table('listing', schema=None) as batch_op:
                batch_op.drop_column('address')
            print("Dropped 'address' column from 'listing' table.")
        else:
            print("'address' column does not exist in 'listing' table.")
    else:
        print("'listing' table does not exist.")

