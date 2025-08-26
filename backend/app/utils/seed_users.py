"""Seed demo users for development."""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, UserPreference
from app.services.auth_service import AuthService


def create_demo_users():
    """Create demo users for development."""
    db = SessionLocal()
    
    try:
        # Demo User 1
        user1_email = "user1@demo.com"
        if not db.query(User).filter(User.email == user1_email).first():
            user1 = User(
                email=user1_email,
                username="user1",
                password_hash=AuthService.get_password_hash("Demo123!"),
                display_name="Demo User One",
                bio="I'm the first demo user for testing",
                is_active=True,
                is_verified=True  # Pre-verified for demo
            )
            db.add(user1)
            db.flush()
            
            # Add preferences for user1
            prefs1 = UserPreference(
                user_id=user1.id,
                theme="light",
                default_grid_size=5
            )
            db.add(prefs1)
            print(f"✅ Created demo user: {user1_email} / password: Demo123!")
        else:
            print(f"ℹ️  User {user1_email} already exists")
        
        # Demo User 2
        user2_email = "user2@demo.com"
        if not db.query(User).filter(User.email == user2_email).first():
            user2 = User(
                email=user2_email,
                username="user2",
                password_hash=AuthService.get_password_hash("Demo123!"),
                display_name="Demo User Two",
                bio="I'm the second demo user for testing",
                is_active=True,
                is_verified=True  # Pre-verified for demo
            )
            db.add(user2)
            db.flush()
            
            # Add preferences for user2
            prefs2 = UserPreference(
                user_id=user2.id,
                theme="dark",
                default_grid_size=3
            )
            db.add(prefs2)
            print(f"✅ Created demo user: {user2_email} / password: Demo123!")
        else:
            print(f"ℹ️  User {user2_email} already exists")
        
        db.commit()
        print("\n📝 Demo Users:")
        print("  Email: user1@demo.com | Password: Demo123!")
        print("  Email: user2@demo.com | Password: Demo123!")
        
    except Exception as e:
        print(f"❌ Error creating demo users: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_demo_users()