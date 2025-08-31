"""Tests for privacy-focused hash-based authentication system."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.privacy_auth_service import PrivacyAuthService

client = TestClient(app)


class TestPrivacyAuthSystem:
    """Test privacy-focused authentication system."""
    
    def test_account_hash_generation(self):
        """Test account hash generation follows security requirements."""
        auth_service = PrivacyAuthService()
        
        # Generate multiple hashes
        hashes = [auth_service.generate_account_hash() for _ in range(100)]
        
        # All hashes should be unique
        assert len(set(hashes)) == 100
        
        # All hashes should be 16 characters
        for hash_val in hashes:
            assert len(hash_val) == 16
            assert auth_service.is_valid_account_hash(hash_val)
    
    def test_account_hash_validation(self):
        """Test account hash validation."""
        auth_service = PrivacyAuthService()
        
        # Valid hashes
        valid_hashes = ["4a8c9f2d1e7b3c6a", "1234567890abcdef", "aaaaaaaaaaaaaaaa"]
        for hash_val in valid_hashes:
            assert auth_service.is_valid_account_hash(hash_val)
        
        # Invalid hashes
        invalid_hashes = [
            "",  # Empty
            "123",  # Too short
            "4a8c9f2d1e7b3c6a1",  # Too long
            "4a8c9f2d1e7b3c6g",  # Invalid hex character
            "4a8c 9f2d1e7b3c6a",  # Contains space
            None,  # None value
        ]
        for hash_val in invalid_hashes:
            assert not auth_service.is_valid_account_hash(hash_val)
    
    def test_anonymous_account_creation(self):
        """Test creating anonymous accounts."""
        response = client.post("/api/v1/auth/account/create", json={})
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return authentication tokens
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # Should return user info
        assert "user" in data
        user = data["user"]
        assert "account_hash" in user
        assert len(user["account_hash"]) == 16
        assert user["is_anonymous"] is True
        assert user["username"].startswith("user_")
    
    def test_hash_based_login(self):
        """Test login with account hash only."""
        # First create an account
        create_response = client.post("/api/v1/auth/account/create", json={})
        assert create_response.status_code == 200
        create_data = create_response.json()
        account_hash = create_data["user"]["account_hash"]
        
        # Now login with the hash
        login_response = client.post(
            "/api/v1/auth/account/login",
            json={"account_hash": account_hash}
        )
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        
        # Should return new tokens
        assert "access_token" in login_data
        assert "refresh_token" in login_data
        assert login_data["user"]["account_hash"] == account_hash
    
    def test_login_with_invalid_hash(self):
        """Test login fails with invalid hash."""
        response = client.post(
            "/api/v1/auth/account/login",
            json={"account_hash": "invalid_hash_123"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_with_nonexistent_hash(self):
        """Test login fails with nonexistent but valid hash."""
        response = client.post(
            "/api/v1/auth/account/login", 
            json={"account_hash": "1111111111111111"}  # Valid format, doesn't exist
        )
        
        assert response.status_code == 401  # Unauthorized
    
    def test_protected_endpoints_require_auth(self):
        """Test protected endpoints require valid authentication."""
        response = client.get("/api/v1/auth/account/me")
        assert response.status_code == 401
        
        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/account/me", headers=headers)
        assert response.status_code == 401
    
    def test_token_refresh(self):
        """Test token refresh functionality."""
        # Create account and get tokens
        create_response = client.post("/api/v1/auth/account/create", json={})
        create_data = create_response.json()
        refresh_token = create_data["refresh_token"]
        
        # Refresh the token
        refresh_response = client.post(
            "/api/v1/auth/token/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        assert "access_token" in refresh_data
        assert refresh_data["token_type"] == "bearer"
    
    def test_account_info_privacy_safe(self):
        """Test account info endpoint returns only safe information."""
        # Create account and login
        create_response = client.post("/api/v1/auth/account/create", json={})
        create_data = create_response.json()
        access_token = create_data["access_token"]
        
        # Get account info
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/account/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only contain safe, non-identifying information
        assert "username" in data
        assert "created_at" in data
        assert "is_anonymous" in data
        
        # Should NOT contain sensitive information
        assert "email" not in data
        assert "password_hash" not in data
        assert "id" not in data
        assert "account_hash" not in data  # Even hash should not be exposed
    
    def test_usage_stats_privacy_safe(self):
        """Test usage stats are privacy-safe."""
        # Create account and login
        create_response = client.post("/api/v1/auth/account/create", json={})
        create_data = create_response.json()
        access_token = create_data["access_token"]
        
        # Get usage stats
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/account/stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should contain only aggregated, non-identifying stats
        expected_fields = ["games_played", "total_time_played", "achievements_earned"]
        for field in expected_fields:
            assert field in data
            assert isinstance(data[field], int)
    
    def test_account_deactivation(self):
        """Test account deactivation for privacy compliance."""
        # Create account
        create_response = client.post("/api/v1/auth/account/create", json={})
        create_data = create_response.json()
        access_token = create_data["access_token"]
        account_hash = create_data["user"]["account_hash"]
        
        # Deactivate account
        headers = {"Authorization": f"Bearer {access_token}"}
        deactivate_response = client.post(
            "/api/v1/auth/account/deactivate",
            json={"account_hash": account_hash, "confirm": True},
            headers=headers
        )
        
        assert deactivate_response.status_code == 200
        
        # Should no longer be able to login
        login_response = client.post(
            "/api/v1/auth/account/login",
            json={"account_hash": account_hash}
        )
        assert login_response.status_code == 401


class TestPrivacySecurity:
    """Test privacy and security aspects of the auth system."""
    
    def test_no_email_password_endpoints(self):
        """Test that email/password login endpoints are removed."""
        # These endpoints should not exist in privacy-focused system
        response = client.post("/api/v1/auth/login", json={
            "email": "test@test.com", 
            "password": "password"
        })
        # Should get 404 (not found) since endpoint doesn't exist
        assert response.status_code == 404
        
        response = client.post("/api/v1/auth/register", json={
            "email": "test@test.com",
            "password": "password", 
            "username": "test"
        })
        assert response.status_code == 404
    
    def test_hash_entropy_sufficient(self):
        """Test that account hashes have sufficient entropy."""
        auth_service = PrivacyAuthService()
        
        # Generate many hashes and check for patterns
        hashes = [auth_service.generate_account_hash() for _ in range(1000)]
        
        # Should have high uniqueness (no collisions in 1000)
        assert len(set(hashes)) == 1000
        
        # Check character distribution (should be roughly uniform for hex)
        all_chars = ''.join(hashes)
        char_counts = {}
        for char in '0123456789abcdef':
            char_counts[char] = all_chars.count(char)
        
        # Each hex character should appear roughly 1000 times (16000 total / 16 chars)
        # Allow for some variance (800-1200 range)
        for count in char_counts.values():
            assert 800 <= count <= 1200, f"Character distribution not uniform: {char_counts}"
    
    def test_no_user_enumeration(self):
        """Test that invalid hashes don't leak information about valid ones."""
        # All invalid hash attempts should return the same error
        invalid_hashes = [
            "0000000000000000",  # Valid format, doesn't exist
            "1111111111111111",  # Valid format, doesn't exist  
            "aaaaaaaaaaaaaaaa",  # Valid format, doesn't exist
        ]
        
        responses = []
        for hash_val in invalid_hashes:
            response = client.post(
                "/api/v1/auth/account/login",
                json={"account_hash": hash_val}
            )
            responses.append(response.status_code)
        
        # All should return the same error code (401)
        assert all(code == 401 for code in responses)
    
    def test_timing_attack_resistance(self):
        """Test basic timing attack resistance."""
        import time
        
        # This is a basic test - in production you'd want more sophisticated timing analysis
        times = []
        
        for _ in range(10):
            start = time.time()
            response = client.post(
                "/api/v1/auth/account/login",
                json={"account_hash": "0000000000000000"}
            )
            end = time.time()
            times.append(end - start)
        
        # Response times should be relatively consistent (< 50% variance)
        avg_time = sum(times) / len(times)
        for t in times:
            variance = abs(t - avg_time) / avg_time
            assert variance < 0.5, f"Timing variance too high: {variance}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])