"""empty message

Revision ID: 49810ee574e0
Revises: 22a4b5ae535a
Create Date: 2023-10-19 12:36:59.121058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49810ee574e0'
down_revision = '22a4b5ae535a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('incident',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('description', sa.String(length=500), nullable=False),
    sa.Column('cause', sa.String(length=500), nullable=True),
    sa.Column('resolution', sa.String(length=500), nullable=True),
    sa.Column('projekt_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['projekt_id'], ['projekt.id'], name='fk_incident_projekt_id'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('incident')
    # ### end Alembic commands ###
