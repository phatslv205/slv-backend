"""create transactions table"""

from alembic import op
import sqlalchemy as sa

# ID tự động sinh
def upgrade():
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('txn_id', sa.String(64), unique=True, nullable=False),
        sa.Column('username', sa.String(64), nullable=False),
        sa.Column('amount', sa.String(32), nullable=False),
        sa.Column('package', sa.String(64), nullable=False),
        sa.Column('method', sa.String(64), nullable=False),
        sa.Column('note', sa.Text, nullable=True),
        sa.Column('status', sa.String(32), default='pending'),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )

def downgrade():
    op.drop_table('transactions')
