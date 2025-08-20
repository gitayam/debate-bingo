#!/usr/bin/env python3
"""
Create demo users and generate authentication tokens for testing.
"""
import sys
import os

# Add the backend directory to Python path and change working directory
backend_path = '/Users/admin/Documents/Git/debate-bingo/backend'
sys.path.insert(0, backend_path)
os.chdir(backend_path)

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService

def create_demo_users():
    """Create demo users for testing."""
    
    db: Session = SessionLocal()
    
    try:
        # Demo users to create
        demo_users = [
            {
                "email": "user1@demo.com",
                "username": "user1",
                "password": "demo123",
                "display_name": "Demo User 1"
            },
            {
                "email": "user2@demo.com", 
                "username": "user2",
                "password": "demo123",
                "display_name": "Demo User 2"
            }
        ]
        
        created_users = []
        
        for user_data in demo_users:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == user_data["email"]) | 
                (User.username == user_data["username"])
            ).first()
            
            if existing_user:
                print(f"👤 User {user_data['username']} already exists (ID: {existing_user.id})")
                created_users.append(existing_user)
            else:
                # Create new user
                try:
                    user = AuthService.create_user(
                        db=db,
                        email=user_data["email"],
                        username=user_data["username"],
                        password=user_data["password"],
                        display_name=user_data["display_name"]
                    )
                    print(f"✅ Created user {user.username} (ID: {user.id})")
                    created_users.append(user)
                    
                except Exception as e:
                    print(f"❌ Failed to create user {user_data['username']}: {e}")
        
        print("\n🔑 Generating access tokens...")
        
        # Generate tokens for each user
        for user in created_users:
            try:
                # Create access token
                token = AuthService.create_access_token(
                    data={"sub": str(user.id), "username": user.username}
                )
                
                print(f"\nUser: {user.username} (ID: {user.id})")
                print(f"Token: {token}")
                print(f"Use this token for WebSocket testing")
                
            except Exception as e:
                print(f"❌ Failed to generate token for {user.username}: {e}")
        
        return created_users
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🎭 Creating Demo Users for WebSocket Testing")
    print("=" * 50)
    
    users = create_demo_users()
    
    if users:
        print(f"\n✅ Demo setup complete! Created/found {len(users)} users.")
        print("\n💡 Copy one of the tokens above and use it in your WebSocket test.")
    else:
        print("\n❌ Demo setup failed!")
        sys.exit(1)