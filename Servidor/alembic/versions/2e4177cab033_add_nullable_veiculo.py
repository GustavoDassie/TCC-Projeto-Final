"""add nullable veiculo

Revision ID: 2e4177cab033
Revises: 7a664049ae20
Create Date: 2023-10-23 19:21:12.327087

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '2e4177cab033'
down_revision: Union[str, None] = '7a664049ae20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('acesso', 'veiculo_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('acesso', 'veiculo_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
