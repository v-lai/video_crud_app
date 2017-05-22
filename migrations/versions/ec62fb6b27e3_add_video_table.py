"""add video table

Revision ID: ec62fb6b27e3
Revises: 6271d22b4603
Create Date: 2017-05-21 14:49:35.774219

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec62fb6b27e3'
down_revision = '6271d22b4603'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('videos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('video', sa.VARCHAR(length=50), nullable=False),
    sa.Column('favorite', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('videos')
    # ### end Alembic commands ###