"""empty message

Revision ID: 0a21c3da577f
Revises: d60e16d204f8
Create Date: 2023-10-26 11:06:24.990833

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a21c3da577f'
down_revision = 'd60e16d204f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ltc', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deployment_successful', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ltc', schema=None) as batch_op:
        batch_op.drop_column('deployment_successful')

    # ### end Alembic commands ###
