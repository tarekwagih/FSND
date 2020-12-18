"""Missing Column.

Revision ID: 491937f68a5c
Revises: 4824d20c74ed
Create Date: 2020-12-19 00:37:38.394916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '491937f68a5c'
down_revision = '4824d20c74ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###