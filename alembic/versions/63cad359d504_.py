"""empty message

Revision ID: 63cad359d504
Revises: 5c467baa75dd
Create Date: 2024-08-15 06:12:40.381153

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "63cad359d504"
down_revision: Union[str, None] = "5c467baa75dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("images", sa.Column("hist_vector_bytes", sa.LargeBinary(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("images", "hist_vector_bytes")
    # ### end Alembic commands ###