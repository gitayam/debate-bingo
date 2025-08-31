"""Add privacy-focused hash-based authentication system

Revision ID: privacy_auth_001
Revises: previous_revision
Create Date: 2024-12-20 12:00:00.000000

"""
from typing import Sequence, Union
import secrets

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Boolean, DateTime, Integer


# revision identifiers, used by Alembic.
revision: str = 'privacy_auth_001'
down_revision: Union[str, None] = '927f65a12c67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def generate_account_hash() -> str:
    """Generate a unique account hash."""
    random_bytes = secrets.token_bytes(8)
    return random_bytes.hex()


def upgrade() -> None:
    """Add privacy-focused authentication fields."""
    
    # Add account_hash column
    op.add_column('users', sa.Column('account_hash', sa.String(16), nullable=True, index=True))
    
    # Add privacy fields
    op.add_column('users', sa.Column('is_anonymous', sa.Boolean(), default=True, nullable=False))
    op.add_column('users', sa.Column('deactivated_at', sa.DateTime(), nullable=True))
    
    # Make email nullable for privacy
    op.alter_column('users', 'email', nullable=True)
    
    # Migrate existing users to hash-based system
    bind = op.get_bind()
    session = Session(bind=bind)
    
    # Create a temporary table structure for migration
    users_table = sa.Table(
        'users',
        sa.MetaData(),
        Column('id', Integer, primary_key=True),
        Column('account_hash', String(16)),
        Column('username', String(100)),
        Column('email', String(255)),
        Column('is_anonymous', Boolean),
    )
    
    # Get all existing users
    result = session.execute(sa.select(users_table.c.id, users_table.c.username, users_table.c.email))
    existing_users = result.fetchall()
    
    # Generate account hashes for existing users
    for user in existing_users:
        account_hash = generate_account_hash()
        
        # Ensure uniqueness
        while True:
            existing = session.execute(
                sa.select(users_table.c.id).where(users_table.c.account_hash == account_hash)
            ).first()
            if not existing:
                break
            account_hash = generate_account_hash()
        
        # Update user with account hash
        session.execute(
            sa.update(users_table).where(users_table.c.id == user.id).values(
                account_hash=account_hash,
                is_anonymous=False  # Existing users are not anonymous
            )
        )
    
    session.commit()
    session.close()
    
    # Make account_hash NOT NULL after migration
    op.alter_column('users', 'account_hash', nullable=False)
    
    # Add unique constraint on account_hash
    op.create_unique_constraint('uq_users_account_hash', 'users', ['account_hash'])
    
    # Add index for performance
    op.create_index('ix_users_account_hash', 'users', ['account_hash'])


def downgrade() -> None:
    """Remove privacy-focused authentication fields."""
    
    # Remove constraints and indexes
    op.drop_index('ix_users_account_hash', table_name='users')
    op.drop_constraint('uq_users_account_hash', 'users', type_='unique')
    
    # Remove columns
    op.drop_column('users', 'deactivated_at')
    op.drop_column('users', 'is_anonymous')
    op.drop_column('users', 'account_hash')
    
    # Make email NOT NULL again
    op.alter_column('users', 'email', nullable=False)