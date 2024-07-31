"""added long and lat to listform

Revision ID: a6ca2a3ebb10
Revises: 579b2f1c3b35
Create Date: 2024-07-20 13:03:04.996998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6ca2a3ebb10'
down_revision = '579b2f1c3b35'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('listing', schema=None) as batch_op:
        batch_op.add_column(sa.Column('latitude', sa.Float(), nullable=False))
        batch_op.add_column(sa.Column('longitude', sa.Float(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('listing', schema=None) as batch_op:
        batch_op.drop_column('longitude')
        batch_op.drop_column('latitude')

    # ### end Alembic commands ###