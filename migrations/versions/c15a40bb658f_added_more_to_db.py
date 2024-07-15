"""added more to db

Revision ID: c15a40bb658f
Revises: cc0c39324275
Create Date: 2024-07-15 09:13:14.433246

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c15a40bb658f'
down_revision = 'cc0c39324275'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=255), nullable=True))
        batch_op.drop_column('password')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', mysql.VARCHAR(length=60), nullable=False))
        batch_op.drop_column('password_hash')

    # ### end Alembic commands ###
