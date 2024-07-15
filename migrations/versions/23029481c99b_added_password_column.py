"""Added password column

Revision ID: 23029481c99b
Revises: c15a40bb658f
Create Date: 2024-07-15 11:28:01.249807

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '23029481c99b'
down_revision = 'c15a40bb658f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(length=255), nullable=False))
        batch_op.drop_column('password_hash')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', mysql.VARCHAR(length=255), nullable=True))
        batch_op.drop_column('password')

    # ### end Alembic commands ###
