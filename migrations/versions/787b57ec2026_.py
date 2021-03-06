"""empty message

Revision ID: 787b57ec2026
Revises: 173dfa296539
Create Date: 2019-10-27 13:23:49.792658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '787b57ec2026'
down_revision = '173dfa296539'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('historical_reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('asin', sa.String(length=20), nullable=False),
    sa.Column('helpful_rating', sa.Integer(), nullable=True),
    sa.Column('total_helpful_rating', sa.Integer(), nullable=True),
    sa.Column('review_rating', sa.Integer(), nullable=True),
    sa.Column('review_text', sa.TEXT(), nullable=True),
    sa.Column('summary_text', sa.String(length=15000), nullable=True),
    sa.Column('reviewer_name', sa.String(length=200), nullable=True),
    sa.Column('reviewer_id', sa.String(length=200), nullable=True),
    sa.Column('date_time', sa.DateTime(), nullable=True),
    sa.Column('unix_timestamp', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_historical_reviews_asin'), 'historical_reviews', ['asin'], unique=False)
    op.create_table('live_reviews',
    sa.Column('reviewer_username', sa.String(length=200), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('asin', sa.String(length=20), nullable=False),
    sa.Column('review_rating', sa.Integer(), nullable=True),
    sa.Column('review_text', sa.TEXT(), nullable=True),
    sa.Column('date_time', sa.DateTime(), nullable=True),
    sa.Column('unix_timestamp', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['reviewer_username'], ['users.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.drop_index('username', table_name='users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('username', 'users', ['username'], unique=True)
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('live_reviews')
    op.drop_index(op.f('ix_historical_reviews_asin'), table_name='historical_reviews')
    op.drop_table('historical_reviews')
    # ### end Alembic commands ###
