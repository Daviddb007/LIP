"""Add SRIE fields, contexto, actores, beneficiarios

Revision ID: 5b6a5f24967e
Revises: 6ee3994227d4
Create Date: 2026-07-07 05:53:14.247133

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b6a5f24967e'
down_revision = '6ee3994227d4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('participaciones', schema=None) as batch_op:
        batch_op.add_column(sa.Column('contexto_ciudadano', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('actores_responsables', sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column('beneficiarios', sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column('srie_pilar', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('srie_urgencia', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('srie_impacto', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('srie_explicacion', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('participaciones', schema=None) as batch_op:
        batch_op.drop_column('srie_explicacion')
        batch_op.drop_column('srie_impacto')
        batch_op.drop_column('srie_urgencia')
        batch_op.drop_column('srie_pilar')
        batch_op.drop_column('beneficiarios')
        batch_op.drop_column('actores_responsables')
        batch_op.drop_column('contexto_ciudadano')
