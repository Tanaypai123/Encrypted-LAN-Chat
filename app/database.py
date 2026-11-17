"""
Database Management Module for Encrypted LAN Chat & File Sharing.
Handles SQLite initialization, migrations, parameterized queries, and thread safety.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone

from config import DATABASE_FILE, BASE_DIR

class DatabaseManager:
    """Thread-safe SQLite database manager using parameterized queries."""

    _instances: Dict[str, "DatabaseManager"] = {}
    _lock = threading.Lock()

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DATABASE_FILE
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self.init_db()

    @classmethod
    def get_instance(cls, db_path: Optional[Path] = None) -> "DatabaseManager":
        path_str = str(db_path or DATABASE_FILE)
        with cls._lock:
            if path_str not in cls._instances:
                cls._instances[path_str] = cls(db_path)
            return cls._instances[path_str]

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create a thread-local SQLite connection."""
        if not hasattr(self._local, "connection") or self._local.connection is None:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=10.0,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for high concurrency
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            self._local.connection = conn
        return self._local.connection

    def init_db(self):
        """Initialize database tables using schema.sql."""
        schema_path = BASE_DIR / "database" / "schema.sql"
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
        else:
            raise FileNotFoundError(f"Schema file not found at {schema_path}")

        conn = self._get_connection()
        with conn:
            conn.executescript(schema_sql)

    def execute_write(self, query: str, params: Tuple = ()) -> int:
        """Execute an INSERT, UPDATE, or DELETE query and return the last row ID."""
        conn = self._get_connection()
        with conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid

    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def execute_query_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a SELECT query and return a single result dict or None."""
        rows = self.execute_query(query, params)
        return rows[0] if rows else None

    # --- User Accounts & Authentication Queries ---

    def create_user(self, username: str, password_hash: str, salt: str, algorithm: str = "argon2id") -> bool:
        """Register a new user in SQLite."""
        query = """
            INSERT INTO users (username, password_hash, salt, algorithm, created_at, is_active)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
        """
        try:
            self.execute_write(query, (username.strip(), password_hash, salt, algorithm))
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetch user record by username."""
        query = "SELECT * FROM users WHERE username = ? AND is_active = 1"
        return self.execute_query_one(query, (username.strip(),))

    def update_last_login(self, username: str):
        """Update last login timestamp for user."""
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?"
        self.execute_write(query, (username.strip(),))

    def update_user_password(self, username: str, new_hash: str, new_salt: str, algorithm: str = "argon2id") -> bool:
        """Update user password hash and salt."""
        query = "UPDATE users SET password_hash = ?, salt = ?, algorithm = ? WHERE username = ?"
        rows_affected = self.execute_write(query, (new_hash, new_salt, algorithm, username.strip()))
        return rows_affected > 0

    # --- Rate Limiting Operations ---

    def record_auth_attempt(self, identifier: str, success: bool):
        """Record an authentication attempt for rate-limiting."""
        query = "INSERT INTO auth_attempts (identifier, success) VALUES (?, ?)"
        self.execute_write(query, (identifier.strip(), 1 if success else 0))

    def is_rate_limited(self, identifier: str, max_attempts: int = 5, window_seconds: int = 60) -> bool:
        """Check if an identifier has exceeded allowed failed login attempts."""
        cutoff_time = (datetime.now(timezone.utc) - timedelta(seconds=window_seconds)).strftime("%Y-%m-%d %H:%M:%S")
        query = """
            SELECT COUNT(*) as failed_count
            FROM auth_attempts
            WHERE identifier = ? AND success = 0 AND attempt_time >= ?
        """
        result = self.execute_query_one(query, (identifier.strip(), cutoff_time))
        if result and result["failed_count"] >= max_attempts:
            return True
        return False

    def clear_auth_attempts(self, identifier: str):
        """Clear failed attempts for an identifier upon successful authentication."""
        query = "DELETE FROM auth_attempts WHERE identifier = ?"
        self.execute_write(query, (identifier.strip(),))

    # --- Chat Messages Queries ---

    def save_message(self, msg_id: str, sender: str, receiver: str, content: str,
                     is_encrypted: bool = True, status: str = "delivered", timestamp: Optional[str] = None) -> int:
        """Save a chat message to history."""
        if timestamp:
            query = """
                INSERT OR IGNORE INTO messages (msg_id, sender_username, receiver_username, message_content, is_encrypted, timestamp, delivery_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            return self.execute_write(query, (msg_id, sender, receiver, content, 1 if is_encrypted else 0, timestamp, status))
        else:
            query = """
                INSERT OR IGNORE INTO messages (msg_id, sender_username, receiver_username, message_content, is_encrypted, delivery_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            return self.execute_write(query, (msg_id, sender, receiver, content, 1 if is_encrypted else 0, status))

    def get_conversation_history(self, user1: str, user2: str, limit: int = 200) -> List[Dict[str, Any]]:
        """Retrieve conversation history between two users in chronological order."""
        query = """
            SELECT * FROM messages
            WHERE (sender_username = ? AND receiver_username = ?)
               OR (sender_username = ? AND receiver_username = ?)
            ORDER BY timestamp ASC, id ASC
            LIMIT ?
        """
        return self.execute_query(query, (user1, user2, user2, user1, limit))

    def get_all_recent_messages(self, current_user: str, limit: int = 500) -> List[Dict[str, Any]]:
        """Get all messages involving current user."""
        query = """
            SELECT * FROM messages
            WHERE sender_username = ? OR receiver_username = ?
            ORDER BY timestamp ASC
            LIMIT ?
        """
        return self.execute_query(query, (current_user, current_user, limit))

    # --- File Transfer Queries ---

    def record_file_transfer(self, transfer_id: str, filename: str, file_size: int,
                             sender: str, receiver: str, sha256_hash: str,
                             local_path: Optional[str] = None, status: str = "pending") -> int:
        """Record a file transfer attempt."""
        query = """
            INSERT OR REPLACE INTO file_transfers
            (transfer_id, filename, file_size, sender_username, receiver_username, sha256_hash, local_path, status, progress, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.0, CURRENT_TIMESTAMP)
        """
        return self.execute_write(query, (transfer_id, filename, file_size, sender, receiver, sha256_hash, local_path, status))

    def update_file_transfer_progress(self, transfer_id: str, progress: float, status: Optional[str] = None):
        """Update transfer progress (0.0 to 100.0)."""
        if status:
            query = "UPDATE file_transfers SET progress = ?, status = ? WHERE transfer_id = ?"
            self.execute_write(query, (progress, status, transfer_id))
        else:
            query = "UPDATE file_transfers SET progress = ? WHERE transfer_id = ?"
            self.execute_write(query, (progress, transfer_id))

    def complete_file_transfer(self, transfer_id: str, status: str = "completed", local_path: Optional[str] = None):
        """Mark a file transfer as completed or failed."""
        if local_path:
            query = """
                UPDATE file_transfers
                SET status = ?, progress = 100.0, local_path = ?, completed_at = CURRENT_TIMESTAMP
                WHERE transfer_id = ?
            """
            self.execute_write(query, (status, local_path, transfer_id))
        else:
            query = """
                UPDATE file_transfers
                SET status = ?, completed_at = CURRENT_TIMESTAMP
                WHERE transfer_id = ?
            """
            self.execute_write(query, (status, transfer_id))

    def get_transfer_history(self, current_user: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve file transfer history."""
        if current_user:
            query = """
                SELECT * FROM file_transfers
                WHERE sender_username = ? OR receiver_username = ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            return self.execute_query(query, (current_user, current_user, limit))
        else:
            query = "SELECT * FROM file_transfers ORDER BY created_at DESC LIMIT ?"
            return self.execute_query(query, (limit,))

    # --- Connection History ---

    def record_connection(self, server_ip: str, server_port: int, status: str = "connected") -> int:
        """Record client connection to a server."""
        query = "INSERT INTO connection_history (server_ip, server_port, status) VALUES (?, ?, ?)"
        return self.execute_write(query, (server_ip, server_port, status))

    def record_disconnection(self, connection_id: int):
        """Mark a connection session as closed."""
        query = "UPDATE connection_history SET disconnected_at = CURRENT_TIMESTAMP, status = 'disconnected' WHERE id = ?"
        self.execute_write(query, (connection_id,))

    # --- Application Settings ---

    def set_setting(self, key: str, value: str):
        """Upsert application configuration value."""
        query = """
            INSERT INTO application_settings (setting_key, setting_value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value, updated_at = CURRENT_TIMESTAMP
        """
        self.execute_write(query, (key, value))

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Fetch setting value by key."""
        query = "SELECT setting_value FROM application_settings WHERE setting_key = ?"
        res = self.execute_query_one(query, (key,))
        return res["setting_value"] if res else default
