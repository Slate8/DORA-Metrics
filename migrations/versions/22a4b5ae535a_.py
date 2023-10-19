"""empty message

Revision ID: 22a4b5ae535a
Revises: 3a3b0e80b297
Create Date: 2023-10-19 10:03:57.472400

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22a4b5ae535a'
down_revision = '3a3b0e80b297'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cd_metrik', schema=None) as batch_op:
        batch_op.add_column(sa.Column('projekt_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_cd_metrik_projekt_id', 'projekt', ['projekt_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cd_metrik', schema=None) as batch_op:
        batch_op.drop_constraint('fk_cd_metrik_projekt_id', type_='foreignkey')
        batch_op.drop_column('projekt_id')

    # ### end Alembic commands ###
