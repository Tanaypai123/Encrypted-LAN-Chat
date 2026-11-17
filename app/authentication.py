"""
User Authentication and Credential Security Module.
Implements Argon2id / PBKDF2-HMAC-SHA256 password hashing, salt generation,
credential validation, session tracking, and rate limiting.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import os
import re
import secrets
import hashlib
import time
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError, VerificationError
    HAS_ARGON2 = True
except ImportError:
    HAS_ARGON2 = False

from app.database import DatabaseManager
from config import (
    ARGON2_TIME_COST,
    ARGON2_MEMORY_COST,
    ARGON2_PARALLELISM,
    PBKDF2_ITERATIONS,
    AUTH_RATE_LIMIT_ATTEMPTS,
    AUTH_RATE_LIMIT_WINDOW
)

@dataclass
class UserSession:
    """Represents an active authenticated user session."""
    user_id: int
    username: str
    session_token: str
    logged_in_at: float
    lan_ip: str = "127.0.0.1"

class AuthenticationError(Exception):
    """Base exception for authentication failures."""
    pass

class RateLimitExceededError(AuthenticationError):
    """Raised when max failed login attempts are exceeded."""
    pass

class ValidationError(AuthenticationError):
    """Raised when username or password does not meet security criteria."""
    pass

class AuthenticationManager:
    """Manages user registration, credential hashing, login validation, and active sessions."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager.get_instance()
        self._current_session: Optional[UserSession] = None
        if HAS_ARGON2:
            self.ph = PasswordHasher(
                time_cost=ARGON2_TIME_COST,
                memory_cost=ARGON2_MEMORY_COST,
                parallelism=ARGON2_PARALLELISM,
                hash_len=32,
                salt_len=16
            )
        else:
            self.ph = None

    @property
    def current_session(self) -> Optional[UserSession]:
        return self._current_session

    @property
    def is_authenticated(self) -> bool:
        return self._current_session is not None

    def validate_username(self, username: str) -> Tuple[bool, str]:
        """Validate username requirements: 3-30 chars, alphanumeric and underscores."""
        username = username.strip()
        if not username:
            return False, "Username cannot be empty."
        if len(username) < 3 or len(username) > 30:
            return False, "Username must be between 3 and 30 characters."
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            return False, "Username may only contain letters, numbers, and underscores."
        return True, ""

    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password strength: min 8 chars, at least 1 letter and 1 number."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if not any(c.isupper() for c in password):
            return False, "Password must include at least one uppercase letter."
        if not any(c.islower() for c in password):
            return False, "Password must include at least one lowercase letter."
        if not any(c.isdigit() for c in password):
            return False, "Password must include at least one digit."
        return True, ""

    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Hash password using Argon2id with unique salt.
        Fallback to PBKDF2-HMAC-SHA256 if Argon2 is unavailable.
        Returns: (password_hash, salt, algorithm)
        """
        if salt is None:
            salt = secrets.token_hex(16)

        if HAS_ARGON2 and self.ph:
            # Argon2 embeds salt internally, but we also save the external salt identifier
            combined = f"{password}{salt}"
            pwd_hash = self.ph.hash(combined)
            return pwd_hash, salt, "argon2id"
        else:
            # Cryptographic PBKDF2-HMAC-SHA256 with 600,000 iterations
            salt_bytes = salt.encode("utf-8")
            pwd_bytes = password.encode("utf-8")
            derived = hashlib.pbkdf2_hmac(
                "sha256",
                pwd_bytes,
                salt_bytes,
                iterations=PBKDF2_ITERATIONS,
                dklen=32
            )
            pwd_hash = derived.hex()
            return pwd_hash, salt, "pbkdf2_sha256"

    def verify_password(self, password: str, stored_hash: str, salt: str, algorithm: str) -> bool:
        """Verify candidate password against stored hash."""
        if algorithm == "argon2id" and HAS_ARGON2 and self.ph:
            try:
                combined = f"{password}{salt}"
                self.ph.verify(stored_hash, combined)
                return True
            except (VerifyMismatchError, VerificationError):
                return False
        else:
            # Fallback verification with PBKDF2
            salt_bytes = salt.encode("utf-8")
            pwd_bytes = password.encode("utf-8")
            derived = hashlib.pbkdf2_hmac(
                "sha256",
                pwd_bytes,
                salt_bytes,
                iterations=PBKDF2_ITERATIONS,
                dklen=32
            )
            # Constant-time comparison to prevent timing attacks
            return secrets.compare_digest(derived.hex(), stored_hash)

    def register(self, username: str, password: str, confirm_password: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new user account with secure password hashing.
        """
        username = username.strip()

        if confirm_password is not None and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        valid_u, err_u = self.validate_username(username)
        if not valid_u:
            raise ValidationError(err_u)

        valid_p, err_p = self.validate_password(password)
        if not valid_p:
            raise ValidationError(err_p)

        # Check existing user
        existing = self.db.get_user_by_username(username)
        if existing:
            raise ValidationError(f"Username '{username}' is already taken.")

        pwd_hash, salt, algo = self.hash_password(password)
        created = self.db.create_user(username, pwd_hash, salt, algo)
        if not created:
            raise ValidationError("Failed to register user. Username may already exist.")

        user_record = self.db.get_user_by_username(username)
        return {
            "success": True,
            "message": f"User '{username}' registered successfully.",
            "user_id": user_record["id"],
            "username": username
        }

    def login(self, username: str, password: str, lan_ip: str = "127.0.0.1") -> UserSession:
        """
        Authenticate user and establish an active session.
        Applies rate limiting to prevent brute force attacks.
        """
        username = username.strip()

        # Check rate limiting
        if self.db.is_rate_limited(username, max_attempts=AUTH_RATE_LIMIT_ATTEMPTS, window_seconds=AUTH_RATE_LIMIT_WINDOW):
            raise RateLimitExceededError(
                f"Too many failed login attempts for '{username}'. Please wait {AUTH_RATE_LIMIT_WINDOW} seconds."
            )

        user = self.db.get_user_by_username(username)
        if not user:
            self.db.record_auth_attempt(username, success=False)
            raise AuthenticationError("Invalid username or password.")

        is_valid = self.verify_password(
            password=password,
            stored_hash=user["password_hash"],
            salt=user["salt"],
            algorithm=user.get("algorithm", "argon2id")
        )

        if not is_valid:
            self.db.record_auth_attempt(username, success=False)
            raise AuthenticationError("Invalid username or password.")

        # Successful authentication: clear attempts & update last login
        self.db.record_auth_attempt(username, success=True)
        self.db.clear_auth_attempts(username)
        self.db.update_last_login(username)

        # Issue secure cryptographic session token
        token = secrets.token_urlsafe(32)
        session = UserSession(
            user_id=user["id"],
            username=username,
            session_token=token,
            logged_in_at=time.time(),
            lan_ip=lan_ip
        )
        self._current_session = session
        return session

    def logout(self):
        """Terminate the current active session."""
        self._current_session = None

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password after verifying current credentials."""
        user = self.db.get_user_by_username(username)
        if not user:
            raise AuthenticationError("User not found.")

        if not self.verify_password(old_password, user["password_hash"], user["salt"], user.get("algorithm", "argon2id")):
            raise AuthenticationError("Current password incorrect.")

        valid_p, err_p = self.validate_password(new_password)
        if not valid_p:
            raise ValidationError(err_p)

        new_hash, new_salt, algo = self.hash_password(new_password)
        return self.db.update_user_password(username, new_hash, new_salt, algo)
