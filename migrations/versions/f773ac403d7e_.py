"""empty message

Revision ID: f773ac403d7e
Revises: d31aa6b7a6aa
Create Date: 2023-10-20 11:06:05.407591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f773ac403d7e'
down_revision = 'd31aa6b7a6aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ltc',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('projekt_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['projekt_id'], ['projekt.id'], name='fk_ltc_projekt_id'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_ltc_user_id'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ltc')
    # ### end Alembic commands ###