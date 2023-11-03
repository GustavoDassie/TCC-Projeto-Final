"""create database

Revision ID: 7a664049ae20
Revises: 06c8500068ae
Create Date: 2023-10-23 19:14:22.684364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '7a664049ae20'
down_revision: Union[str, None] = '06c8500068ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('usuario',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('senha', sa.String(length=255), nullable=True),
    sa.Column('inserido_em', sa.DATETIME(), server_default=sa.text('now()'), nullable=False),
    sa.Column('ativo', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('funcionario',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('cpf', sa.String(length=255), nullable=True),
    sa.Column('inserido_em', sa.DATETIME(), server_default=sa.text('now()'), nullable=False),
    sa.Column('atualizado_em', sa.DATETIME(), server_default=sa.text('now()'), nullable=False),
    sa.Column('ativo', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('veiculo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('funcionario_id', sa.Integer(), nullable=False),
    sa.Column('placa', sa.String(length=255), nullable=True),
    sa.Column('modelo', sa.String(length=255), nullable=True),
    sa.Column('ano', sa.String(length=255), nullable=True),
    sa.Column('inserido_em', sa.DATETIME(), server_default=sa.text('now()'), nullable=False),
    sa.Column('atualizado_em', sa.DATETIME(), server_default=sa.text('now()'), nullable=False),
    sa.Column('ativo', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['funcionario_id'], ['funcionario.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('acesso',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('inserido_em', sa.DATETIME(), server_default=sa.text('now()'), nullable=False),
    sa.Column('eh_entrada', sa.Boolean(), nullable=False),
    sa.Column('caracteres_detectados', sa.String(length=255), nullable=True),
    sa.Column('veiculo_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['veiculo_id'], ['veiculo.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('image')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('image',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('raw_data', mysql.LONGBLOB(), nullable=False),
    sa.Column('file_name', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('file_ext', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('treated_data', mysql.LONGBLOB(), nullable=True),
    sa.Column('charset', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('insert_date', mysql.DATETIME(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('acesso')
    op.drop_table('veiculo')
    op.drop_table('funcionario')
    op.drop_table('usuario')
    # ### end Alembic commands ###
