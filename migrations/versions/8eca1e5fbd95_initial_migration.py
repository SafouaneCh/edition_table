"""Initial migration

Revision ID: 8eca1e5fbd95
Revises: 
Create Date: 2024-07-18 10:48:42.314704

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8eca1e5fbd95'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('numero', sa.String(length=100), nullable=False),
    sa.Column('date_creation', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('todo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nom_edition', sa.String(length=200), nullable=False),
    sa.Column('type_edition', sa.String(length=20), nullable=False),
    sa.Column('type_envoie', sa.String(length=100), nullable=False),
    sa.Column('nombre_page_destinataire', sa.Integer(), nullable=False),
    sa.Column('nombre_destinataires', sa.Integer(), nullable=False),
    sa.Column('nombre_page', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('lot_entry',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lot_id', sa.Integer(), nullable=False),
    sa.Column('nom_edition', sa.String(length=200), nullable=False),
    sa.Column('type_edition', sa.String(length=20), nullable=False),
    sa.Column('type_envoie', sa.String(length=100), nullable=False),
    sa.Column('nombre_page_destinataire', sa.Integer(), nullable=False),
    sa.Column('nombre_destinataires', sa.Integer(), nullable=False),
    sa.Column('nombre_page', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['lot_id'], ['lot.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lot_entry')
    op.drop_table('todo')
    op.drop_table('lot')
    # ### end Alembic commands ###
