"""Add post_type column

Revision ID: 877829631699
Revises: 
Create Date: 2023-11-26 00:03:16.081756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '877829631699'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    #op.drop_table('likes')
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('post_type', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('_characters', sa.Integer))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('post_type')

    op.create_table('likes',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('current_user', sa.INTEGER(), nullable=False),
    sa.Column('liked_post', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['current_user'], ['profiles.id'], ),
    sa.ForeignKeyConstraint(['liked_post'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###