"""empty message

Revision ID: add98ca63cc5
Revises: 
Create Date: 2022-02-24 17:52:12.142833

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add98ca63cc5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('college',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('email', sa.String(length=60), nullable=False),
    sa.Column('password', sa.String(length=30), nullable=False),
    sa.Column('registered', sa.Date(), nullable=True),
    sa.Column('name', sa.String(length=30), nullable=True),
    sa.Column('surname', sa.String(length=30), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('biography', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('faculty',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.Column('college_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['college_id'], ['college.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sender', sa.Integer(), nullable=False),
    sa.Column('receiver', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['receiver'], ['user.id'], ),
    sa.ForeignKeyConstraint(['sender'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('network',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('link', sa.String(length=30), nullable=False),
    sa.ForeignKeyConstraint(['owner'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_tags',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'tag_id')
    )
    op.create_table('class',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.Column('faculty_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['faculty_id'], ['faculty.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('faculty_members',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('faculty_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['faculty_id'], ['faculty.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'faculty_id')
    )
    op.create_table('class_students',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('class_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['class_id'], ['class.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'class_id')
    )
    op.create_table('coll',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=60), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=True),
    sa.Column('class_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=12), nullable=False),
    sa.ForeignKeyConstraint(['class_id'], ['class.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=60), nullable=False),
    sa.Column('content', sa.String(length=120), nullable=False),
    sa.Column('class_id', sa.Integer(), nullable=True),
    sa.Column('uploader_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=12), nullable=False),
    sa.ForeignKeyConstraint(['class_id'], ['class.id'], ),
    sa.ForeignKeyConstraint(['uploader_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('commenter_id', sa.Integer(), nullable=True),
    sa.Column('coll_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['coll_id'], ['coll.id'], ),
    sa.ForeignKeyConstraint(['commenter_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('favorite_colls',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('coll_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['coll_id'], ['coll.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'coll_id')
    )
    op.create_table('favorite_files',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'file_id')
    )
    op.create_table('liked_colls',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('coll_id', sa.Integer(), nullable=False),
    sa.Column('is_like', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['coll_id'], ['coll.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'coll_id')
    )
    op.create_table('liked_files',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('is_like', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'file_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('liked_files')
    op.drop_table('liked_colls')
    op.drop_table('favorite_files')
    op.drop_table('favorite_colls')
    op.drop_table('comment')
    op.drop_table('file')
    op.drop_table('coll')
    op.drop_table('class_students')
    op.drop_table('faculty_members')
    op.drop_table('class')
    op.drop_table('user_tags')
    op.drop_table('network')
    op.drop_table('message')
    op.drop_table('faculty')
    op.drop_table('user')
    op.drop_table('tag')
    op.drop_table('college')
    # ### end Alembic commands ###