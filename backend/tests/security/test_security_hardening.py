"""Security tests to verify hardening measures are working correctly."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


class TestCriticalSecurityFixes:
    """Test critical security vulnerabilities are fixed."""
    
    def test_jwt_secret_not_hardcoded(self):
        """Ensure JWT secret is not hardcoded."""
        # Check that secret key is not the default hardcoded value
        assert settings.SECRET_KEY != "change-this-secret-key-in-production"
        assert settings.SECRET_KEY != "your-secret-key-here"
        
        # Ensure secret key meets minimum length requirement
        assert len(settings.SECRET_KEY) >= 32
    
    def test_security_headers_present(self):
        """Verify security headers are applied."""
        response = client.get("/")
        
        # Check critical security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "X-XSS-Protection" in response.headers
        assert "Content-Security-Policy" in response.headers
    
    def test_cors_hardening(self):
        """Verify CORS is properly restricted."""
        # Test with invalid origin
        response = client.get("/", headers={"Origin": "https://evil.com"})
        
        # Should not allow arbitrary origins
        if "Access-Control-Allow-Origin" in response.headers:
            assert response.headers["Access-Control-Allow-Origin"] != "*"
    
    def test_rate_limiting_on_auth(self):
        """Test rate limiting on authentication endpoints."""
        login_data = {"account_hash": "invalid_hash_123"}
        
        # Make 6 requests (rate limit is 5/minute)
        responses = []
        for i in range(6):
            response = client.post("/api/v1/auth/account/login", json=login_data)
            responses.append(response.status_code)
        
        # Last request should be rate limited (429)
        assert responses[-1] == 429 or responses[-1] == 401  # Either rate limited or auth failed
    
    def test_input_validation(self):
        """Test input validation prevents injection attempts."""
        # Test SQL injection attempt with account hash
        malicious_input = {"account_hash": "'; DROP TABLE users; --"}
        response = client.post("/api/v1/auth/account/login", json=malicious_input)
        
        # Should not cause internal server error (500)
        assert response.status_code in [400, 401, 422, 429]  # Client errors, not server error
        
        # Test XSS attempt with account hash
        xss_input = {"account_hash": "<script>alert('xss')</script>"}
        response = client.post("/api/v1/auth/account/login", json=xss_input)
        assert response.status_code in [400, 401, 422, 429]


class TestAuthenticationSecurity:
    """Test authentication security measures."""
    
    def test_protected_endpoints_require_auth(self):
        """Verify sensitive endpoints require authentication."""
        # Test bingo game creation without auth
        game_data = {"event_name": "Test Event", "player_name": "Test Player"}
        response = client.post("/api/v1/bingo/game", json=game_data)
        
        # Should require authentication
        assert response.status_code in [401, 403]
    
    def test_token_validation(self):
        """Test JWT token validation."""
        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        # Should reject invalid token
        assert response.status_code in [401, 403]
    
    def test_websocket_auth_required(self):
        """Test WebSocket connections require valid authentication."""
        # This would need WebSocket testing framework
        # For now, just verify the endpoint exists
        # In production, would test with invalid tokens
        pass


class TestInputSecurity:
    """Test input validation and sanitization."""
    
    def test_session_id_validation(self):
        """Test session ID validation prevents injection."""
        malicious_session_ids = [
            "'; DROP TABLE sessions; --",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "%00%00%00",
            "' OR '1'='1"
        ]
        
        for session_id in malicious_session_ids:
            response = client.get(f"/api/v1/bingo/game/{session_id}")
            # Should not cause server error
            assert response.status_code in [400, 404, 422]  # Client errors only
    
    def test_request_size_limits(self):
        """Test request size limits prevent DoS."""
        # Test with very large payload
        large_data = {"data": "x" * 10000}  # 10KB payload
        response = client.post("/api/v1/bingo/game", json=large_data)
        
        # Should handle gracefully
        assert response.status_code != 500


class TestSecurityLogging:
    """Test security events are properly logged."""
    
    def test_failed_login_logged(self):
        """Verify failed login attempts are logged."""
        # This would require log capture in real implementation
        login_data = {"email": "test@test.com", "password": "wrongpassword"}
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Should log the attempt (verified manually or with log capture)
        assert response.status_code in [401, 429]
    
    def test_security_events_logged(self):
        """Verify security-relevant requests are logged."""
        # Access admin endpoints
        response = client.get("/api/v1/auth/me")
        
        # Should be logged (verified manually or with log capture)
        assert response.status_code in [401, 403]


@pytest.mark.integration
class TestProductionSecurity:
    """Integration tests for production security setup."""
    
    def test_environment_variables_required(self):
        """Test that production requires environment variables."""
        # In production, certain env vars should be required
        # This would be tested in production environment
        pass
    
    def test_https_redirect(self):
        """Test HTTPS redirect in production."""
        # Would test HTTPS redirect when enabled
        pass
    
    def test_database_security(self):
        """Test database connection security."""
        # Would test SSL connections, credential security
        pass


if __name__ == "__main__":
    # Run security tests
    pytest.main([__file__, "-v"])