"""empty message

Revision ID: 3011b84cd898
Revises: 
Create Date: 2023-10-16 12:47:17.537932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3011b84cd898'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cd_metrik',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('dora_daten')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dora_daten',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user', sa.VARCHAR(length=200), nullable=True),
    sa.Column('content', sa.VARCHAR(length=500), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('cd_metrik')
    # ### end Alembic commands ###