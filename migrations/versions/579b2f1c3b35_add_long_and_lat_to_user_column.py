"""add long and lat to user column

Revision ID: 579b2f1c3b35
Revises: 6013f58bc3dc
Create Date: 2024-07-18 17:01:19.706534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '579b2f1c3b35'
down_revision = '6013f58bc3dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('latitude', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('longitude', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('longitude')
        batch_op.drop_column('latitude')

    # ### end Alembic commands ###