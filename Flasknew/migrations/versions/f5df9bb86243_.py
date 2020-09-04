"""empty message

Revision ID: f5df9bb86243
Revises: 76be3ef0f72f
Create Date: 2019-10-07 20:25:26.299540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5df9bb86243'
down_revision = '76be3ef0f72f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('curriculum',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('c_id', sa.String(length=32), nullable=True),
    sa.Column('c_name', sa.String(length=32), nullable=True),
    sa.Column('c_time', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('leave',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('request_id', sa.Integer(), nullable=True),
    sa.Column('request_name', sa.String(length=32), nullable=True),
    sa.Column('request_type', sa.String(length=32), nullable=True),
    sa.Column('request_start_time', sa.String(length=32), nullable=True),
    sa.Column('request_end_time', sa.String(length=32), nullable=True),
    sa.Column('request_description', sa.Text(), nullable=True),
    sa.Column('request_phone', sa.String(length=32), nullable=True),
    sa.Column('request_status', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('leave')
    op.drop_table('curriculum')
    # ### end Alembic commands ###