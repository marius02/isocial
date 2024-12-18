"""revised timestamp fields

Revision ID: a5c7fc33bef1
Revises: 641d444f8a43
Create Date: 2024-03-15 06:54:50.535834

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a5c7fc33bef1'
down_revision: Union[str, None] = '641d444f8a43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('all_chats', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.TIMESTAMP(timezone=True),
               existing_nullable=True,
               existing_server_default=sa.text('now()'))
    op.alter_column('responses', 'date',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.TIMESTAMP(timezone=True),
               existing_nullable=True,
               existing_server_default=sa.text('now()'))
    op.alter_column('usersubscription', 'buy_date',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.TIMESTAMP(timezone=True),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('usersubscription', 'buy_date',
               existing_type=sa.TIMESTAMP(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('responses', 'date',
               existing_type=sa.TIMESTAMP(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('now()'))
    op.alter_column('all_chats', 'created_at',
               existing_type=sa.TIMESTAMP(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True,
               existing_server_default=sa.text('now()'))
    # ### end Alembic commands ###
