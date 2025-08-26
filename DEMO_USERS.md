# Demo Users for Development

## Quick Login Credentials

Two demo users are pre-configured for development and testing:

### Demo User 1
- **Email:** `user1@demo.com`
- **Password:** `Demo123!`
- **Username:** `user1`
- **Display Name:** Demo User One

### Demo User 2
- **Email:** `user2@demo.com`
- **Password:** `Demo123!`
- **Username:** `user2`
- **Display Name:** Demo User Two

## How to Use

### Via UI:
1. Visit http://localhost:3745
2. Click "Sign In" in the header
3. In the login modal, you'll see a blue box with demo credentials
4. Click on either demo user to auto-fill the login form
5. Click "Sign In" to login

### Via API:
```bash
# Login as User 1
curl -X POST http://localhost:8745/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@demo.com",
    "password": "Demo123!"
  }'

# Login as User 2
curl -X POST http://localhost:8745/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user2@demo.com",
    "password": "Demo123!"
  }'
```

## Recreate Demo Users

If you need to recreate the demo users:

```bash
docker-compose exec backend python -m app.utils.seed_users
```

## Features for Testing

Both demo users have:
- Pre-verified email addresses
- Active accounts
- Different theme preferences (User 1: light, User 2: dark)
- Different default grid sizes (User 1: 5x5, User 2: 3x3)
- Profile bios for testing profile display

These users are perfect for:
- Testing authentication flow
- Testing user-specific features
- Testing multi-user scenarios
- Developing social features
- Testing scoreboards and competitions