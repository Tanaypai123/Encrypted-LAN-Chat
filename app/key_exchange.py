"""
Key Exchange Module using Elliptic Curve Diffie-Hellman (X25519) and HKDF-SHA256.
Enables end-to-end forward-secure key agreement between LAN peers.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import base64
import time
import threading
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from config import AES_KEY_SIZE, HKDF_INFO

@dataclass
class PeerSessionKey:
    """Stores established session key and metadata for a peer."""
    peer_username: str
    session_key: bytes
    established_at: float
    is_initiator: bool

class KeyExchangeSession:
    """Represents a single X25519 ephemeral key agreement handshake."""

    def __init__(self):
        # Generate fresh ephemeral X25519 private key
        self.private_key = x25519.X25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        self.created_at = time.time()

    def get_public_key_bytes(self) -> bytes:
        """Export raw 32-byte public key."""
        return self.public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw
        )

    def get_public_key_b64(self) -> str:
        """Export base64 encoded public key for network transport."""
        return base64.b64encode(self.get_public_key_bytes()).decode("utf-8")

    def derive_session_key(self, peer_public_key_bytes: bytes, salt: Optional[bytes] = None) -> bytes:
        """
        Derive AES-256 session key from peer public key using HKDF-SHA256.
        """
        if len(peer_public_key_bytes) != 32:
            raise ValueError(f"X25519 public key must be 32 bytes. Got {len(peer_public_key_bytes)} bytes.")

        peer_pub_key = x25519.X25519PublicKey.from_public_bytes(peer_public_key_bytes)
        # Compute raw Curve25519 shared secret
        shared_secret = self.private_key.exchange(peer_pub_key)

        # Expand shared secret using HKDF with SHA-256
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=AES_KEY_SIZE,
            salt=salt,
            info=HKDF_INFO,
        )
        derived_key = hkdf.derive(shared_secret)
        return derived_key

class KeyExchangeManager:
    """
    Thread-safe manager for peer session keys and active handshakes.
    Maintains end-to-end encrypted sessions between local user and LAN peers.
    """

    def __init__(self):
        self._lock = threading.Lock()
        # Pending handshake sessions: {peer_username: KeyExchangeSession}
        self._pending_handshakes: Dict[str, KeyExchangeSession] = {}
        # Established session keys: {peer_username: PeerSessionKey}
        self._established_sessions: Dict[str, PeerSessionKey] = {}

    def initiate_handshake(self, peer_username: str) -> str:
        """
        Generate ephemeral key pair for peer and return base64 public key.
        """
        with self._lock:
            session = KeyExchangeSession()
            self._pending_handshakes[peer_username] = session
            return session.get_public_key_b64()

    def handle_handshake_init(self, peer_username: str, peer_pub_key_b64: str) -> Tuple[str, bytes]:
        """
        Process incoming handshake initiation from a peer:
        Generates own ephemeral pair, derives key, and returns (own_pub_key_b64, session_key).
        """
        peer_pub_bytes = base64.b64decode(peer_pub_key_b64)
        session = KeyExchangeSession()
        derived_key = session.derive_session_key(peer_pub_bytes)

        with self._lock:
            self._established_sessions[peer_username] = PeerSessionKey(
                peer_username=peer_username,
                session_key=derived_key,
                established_at=time.time(),
                is_initiator=False
            )
            # Remove any stale pending handshake
            self._pending_handshakes.pop(peer_username, None)

        return session.get_public_key_b64(), derived_key

    def handle_handshake_reply(self, peer_username: str, peer_pub_key_b64: str) -> bytes:
        """
        Process handshake reply from peer to complete key exchange.
        """
        peer_pub_bytes = base64.b64decode(peer_pub_key_b64)

        with self._lock:
            pending = self._pending_handshakes.pop(peer_username, None)
            if not pending:
                raise KeyError(f"No pending key exchange found for peer '{peer_username}'.")

            derived_key = pending.derive_session_key(peer_pub_bytes)
            self._established_sessions[peer_username] = PeerSessionKey(
                peer_username=peer_username,
                session_key=derived_key,
                established_at=time.time(),
                is_initiator=True
            )
            return derived_key

    def get_session_key(self, peer_username: str) -> Optional[bytes]:
        """Retrieve established symmetric session key for a peer."""
        with self._lock:
            session = self._established_sessions.get(peer_username)
            return session.session_key if session else None

    def has_session_key(self, peer_username: str) -> bool:
        """Check if secure session is currently established with peer."""
        with self._lock:
            return peer_username in self._established_sessions

    def remove_session(self, peer_username: str):
        """Remove session key on disconnect or logout."""
        with self._lock:
            self._established_sessions.pop(peer_username, None)
            self._pending_handshakes.pop(peer_username, None)

    def clear_all(self):
        """Reset all cryptographic sessions."""
        with self._lock:
            self._established_sessions.clear()
            self._pending_handshakes.clear()
