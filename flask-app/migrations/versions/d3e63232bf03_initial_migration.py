"""Initial migration.

Revision ID: d3e63232bf03
Revises: 
Create Date: 2024-05-10 10:16:31.809725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3e63232bf03'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fullname', sa.String(length=200), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('email', sa.String(length=200), nullable=False),
    sa.Column('id_passport_no', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('profile_picture', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('corruption_reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('govt_agency', sa.String(length=200), nullable=False),
    sa.Column('county', sa.String(length=200), nullable=False),
    sa.Column('location_url', sa.String(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.String(length=600), nullable=False),
    sa.Column('media', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('password_reset_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=100), nullable=False),
    sa.Column('expiration', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('public_petitions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('govt_agency', sa.String(length=200), nullable=False),
    sa.Column('county', sa.String(length=200), nullable=False),
    sa.Column('location_url', sa.String(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.String(length=600), nullable=False),
    sa.Column('media', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('corruption_resolutions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('justification', sa.String(), nullable=False),
    sa.Column('additional_comments', sa.String(length=600), nullable=True),
    sa.Column('record_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['record_id'], ['corruption_reports.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('petition_resolutions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('justification', sa.String(), nullable=False),
    sa.Column('additional_comments', sa.String(length=600), nullable=True),
    sa.Column('record_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['record_id'], ['public_petitions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('petition_resolutions')
    op.drop_table('corruption_resolutions')
    op.drop_table('public_petitions')
    op.drop_table('password_reset_token')
    op.drop_table('corruption_reports')
    op.drop_table('users')
    # ### end Alembic commands ###
