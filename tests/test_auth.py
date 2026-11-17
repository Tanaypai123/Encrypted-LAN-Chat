"""
Unit Tests for Authentication and Database.
Tests password hashing (Argon2id / PBKDF2), rate limiting, registration, and login.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import pytest
import tempfile
from pathlib import Path

from app.database import DatabaseManager
from app.authentication import (
    AuthenticationManager,
    ValidationError,
    AuthenticationError,
    RateLimitExceededError
)

@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test.db"
        db = DatabaseManager(db_path)
        yield db

@pytest.fixture
def auth_mgr(temp_db):
    return AuthenticationManager(temp_db)

def test_user_registration_success(auth_mgr):
    result = auth_mgr.register("testuser1", "Password123")
    assert result["success"] is True
    assert result["username"] == "testuser1"

def test_duplicate_registration_fails(auth_mgr):
    auth_mgr.register("duplicate_user", "SecurePass1")
    with pytest.raises(ValidationError) as exc:
        auth_mgr.register("duplicate_user", "SecurePass1")
    assert "already taken" in str(exc.value)

def test_weak_password_rejection(auth_mgr):
    # Too short
    with pytest.raises(ValidationError):
        auth_mgr.register("user_short", "Pass1")
    # No digit
    with pytest.raises(ValidationError):
        auth_mgr.register("user_nodigit", "PasswordOnly")
    # No uppercase
    with pytest.raises(ValidationError):
        auth_mgr.register("user_nolower", "password123")

def test_invalid_username_rejection(auth_mgr):
    # Invalid characters
    with pytest.raises(ValidationError):
        auth_mgr.register("user@invalid!", "Password123")
    # Too short
    with pytest.raises(ValidationError):
        auth_mgr.register("ab", "Password123")

def test_successful_login(auth_mgr):
    auth_mgr.register("alice", "AliceSecret99")
    session = auth_mgr.login("alice", "AliceSecret99", lan_ip="192.168.1.10")
    assert session.username == "alice"
    assert session.session_token is not None
    assert auth_mgr.is_authenticated is True

def test_invalid_password_rejection(auth_mgr):
    auth_mgr.register("bob", "BobSecret99")
    with pytest.raises(AuthenticationError):
        auth_mgr.login("bob", "WrongPassword123")

def test_rate_limiting_brute_force_prevention(auth_mgr):
    auth_mgr.register("charlie", "CharliePass1")
    # Fail 5 times
    for _ in range(5):
        try:
            auth_mgr.login("charlie", "WrongGuess123")
        except AuthenticationError:
            pass

    # 6th attempt should raise RateLimitExceededError
    with pytest.raises(RateLimitExceededError):
        auth_mgr.login("charlie", "CharliePass1")
