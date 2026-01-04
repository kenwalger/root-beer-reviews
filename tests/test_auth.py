"""Tests for authentication utilities and routes."""
import pytest
from fastapi import status
from httpx import AsyncClient
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    authenticate_admin,
    get_admin_user_by_email,
)
from app.database import get_database


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """Tests for password hashing and verification."""
    
    def test_get_password_hash(self):
        """Test password hashing produces a hash."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash format
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password("wrongpassword", hashed) is False
    
    def test_password_hash_truncates_long_passwords(self):
        """Test that passwords longer than 72 bytes are truncated."""
        # Create a password longer than 72 bytes
        long_password = "a" * 100
        hashed = get_password_hash(long_password)
        
        # Should still verify correctly (truncated to 72 bytes)
        assert verify_password(long_password, hashed) is True


@pytest.mark.unit
@pytest.mark.auth
class TestJWTTokens:
    """Tests for JWT token creation and decoding."""
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_access_token_valid(self):
        """Test decoding a valid JWT token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded["sub"] == "test@example.com"
        assert "exp" in decoded
    
    def test_decode_access_token_invalid(self):
        """Test decoding an invalid JWT token raises exception."""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("invalid.token.here")
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
@pytest.mark.auth
class TestAdminUserOperations:
    """Tests for admin user database operations."""
    
    @pytest.mark.asyncio
    async def test_get_admin_user_by_email_exists(self, test_db: None, admin_user: dict[str, str]):
        """Test getting admin user by email when user exists."""
        user = await get_admin_user_by_email(admin_user["email"])
        
        assert user is not None
        assert user.email == admin_user["email"]
        assert user.is_active is True
    
    @pytest.mark.asyncio
    async def test_get_admin_user_by_email_not_exists(self, test_db: None):
        """Test getting admin user by email when user doesn't exist."""
        user = await get_admin_user_by_email("nonexistent@example.com")
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_admin_success(self, test_db: None, admin_user: dict[str, str]):
        """Test successful admin authentication."""
        user = await authenticate_admin(admin_user["email"], admin_user["password"])
        
        assert user is not None
        assert user.email == admin_user["email"]
    
    @pytest.mark.asyncio
    async def test_authenticate_admin_wrong_password(self, test_db: None, admin_user: dict[str, str]):
        """Test admin authentication with wrong password."""
        user = await authenticate_admin(admin_user["email"], "wrongpassword")
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_admin_nonexistent_user(self, test_db: None):
        """Test admin authentication with nonexistent user."""
        user = await authenticate_admin("nonexistent@example.com", "password")
        
        assert user is None


@pytest.mark.integration
@pytest.mark.auth
class TestAuthRoutes:
    """Tests for authentication routes."""
    
    @pytest.mark.asyncio
    async def test_login_page_loads(self, client: AsyncClient):
        """Test that login page loads successfully."""
        response = await client.get("/admin/login")
        
        assert response.status_code == status.HTTP_200_OK
        assert "login" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, admin_user: dict[str, str]):
        """Test successful login."""
        response = await client.post(
            "/admin/login",
            data={
                "email": admin_user["email"],
                "password": admin_user["password"],
            },
            follow_redirects=False,
        )
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_200_OK]
        # Check for authentication cookie
        assert "admin_token" in response.cookies
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, admin_user: dict[str, str]):
        """Test login with wrong password."""
        response = await client.post(
            "/admin/login",
            data={
                "email": admin_user["email"],
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "admin_token" not in response.cookies
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user."""
        response = await client.post(
            "/admin/login",
            data={
                "email": "nonexistent@example.com",
                "password": "password",
            },
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_logout(self, authenticated_client: AsyncClient):
        """Test logout functionality."""
        response = await authenticated_client.get("/admin/logout", follow_redirects=False)
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        # Cookie should be deleted (empty value or max-age=0)
        cookies = response.cookies
        assert "admin_token" not in cookies or cookies.get("admin_token") == ""
    
    @pytest.mark.asyncio
    async def test_get_current_admin_invalid_token(self, client: AsyncClient):
        """Test get_current_admin with invalid token."""
        from fastapi import HTTPException
        
        # Set invalid token in cookies
        client.cookies.set("admin_token", "invalid_token")
        
        # Try to access a protected route - should raise HTTPException
        response = await client.get("/admin", follow_redirects=False)
        
        # Should redirect or return 401
        assert response.status_code in [
            status.HTTP_303_SEE_OTHER,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_307_TEMPORARY_REDIRECT,
        ]
    
    @pytest.mark.asyncio
    async def test_get_admin_optional_invalid_token(self, client: AsyncClient):
        """Test get_admin_optional with invalid token - should not break public routes."""
        # Set invalid token in cookies
        client.cookies.set("admin_token", "invalid_token")
        
        # Access a public route - should work fine even with invalid token
        response = await client.get("/")
        
        # Should succeed (public route doesn't require auth)
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_verify_password_exception_handling(self):
        """Test verify_password handles exceptions gracefully."""
        from app.auth import verify_password
        
        # Test with invalid hash format
        result = verify_password("password", "invalid_hash")
        assert result is False
        
        # Test with empty password
        result = verify_password("", "some_hash")
        assert result is False

