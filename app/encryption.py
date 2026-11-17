"""
Cryptographic Operations Module.
Provides AES-256-GCM authenticated encryption/decryption, secure random nonce generation,
file chunk encryption, and SHA-256 hash validation.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import os
import base64
import hashlib
import secrets
from typing import Tuple, Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

from config import (
    AES_KEY_SIZE,
    AES_GCM_NONCE_SIZE,
    FILE_CHUNK_SIZE
)

class CryptographyError(Exception):
    """Base exception for cryptographic errors."""
    pass

class DecryptionError(CryptographyError):
    """Raised when ciphertext cannot be decrypted or authentication tag fails."""
    pass

class TamperedMessageError(DecryptionError):
    """Raised when message integrity verification fails due to tampering."""
    pass

def generate_random_bytes(length: int = 32) -> bytes:
    """Generate cryptographically secure random bytes."""
    return secrets.token_bytes(length)

def generate_symmetric_key() -> bytes:
    """Generate a random 256-bit (32 bytes) AES key."""
    return AESGCM.generate_key(bit_length=256)

def encrypt_message(plaintext: str, key: bytes, associated_data: Optional[bytes] = None) -> Dict[str, str]:
    """
    Encrypt a text message using AES-256-GCM with a fresh 96-bit nonce.
    Returns dictionary with base64 encoded 'ciphertext' and 'nonce'.
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"AES key must be {AES_KEY_SIZE} bytes (256 bits). Got {len(key)} bytes.")

    # Generate a fresh 12-byte nonce for every operation
    nonce = os.urandom(AES_GCM_NONCE_SIZE)
    aesgcm = AESGCM(key)

    plaintext_bytes = plaintext.encode("utf-8")
    # AESGCM.encrypt appends the 16-byte authentication tag to the ciphertext
    ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, associated_data)

    return {
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
        "nonce": base64.b64encode(nonce).decode("utf-8")
    }

def decrypt_message(encrypted_data: Dict[str, str], key: bytes, associated_data: Optional[bytes] = None) -> str:
    """
    Decrypt an AES-256-GCM encrypted message.
    Verifies authentication tag and raises TamperedMessageError if modified.
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"AES key must be {AES_KEY_SIZE} bytes (256 bits). Got {len(key)} bytes.")

    try:
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        nonce = base64.b64decode(encrypted_data["nonce"])
    except (KeyError, ValueError, Exception) as e:
        raise DecryptionError(f"Malformed encrypted payload: {e}")

    if len(nonce) != AES_GCM_NONCE_SIZE:
        raise DecryptionError(f"Invalid nonce length: expected {AES_GCM_NONCE_SIZE}, got {len(nonce)}")

    aesgcm = AESGCM(key)
    try:
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, associated_data)
        return decrypted_bytes.decode("utf-8")
    except InvalidTag:
        raise TamperedMessageError("Decryption failed: Authentication tag verification failed! The message may have been tampered with or corrupted.")
    except Exception as e:
        raise DecryptionError(f"Decryption error: {e}")

def encrypt_bytes(raw_bytes: bytes, key: bytes, associated_data: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """
    Encrypt raw binary data using AES-256-GCM.
    Returns: (ciphertext_with_tag, nonce)
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"AES key must be {AES_KEY_SIZE} bytes.")
    nonce = os.urandom(AES_GCM_NONCE_SIZE)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, raw_bytes, associated_data)
    return ciphertext, nonce

def decrypt_bytes(ciphertext: bytes, nonce: bytes, key: bytes, associated_data: Optional[bytes] = None) -> bytes:
    """
    Decrypt raw binary data with AES-256-GCM and verify tag.
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"AES key must be {AES_KEY_SIZE} bytes.")
    if len(nonce) != AES_GCM_NONCE_SIZE:
        raise DecryptionError(f"Invalid nonce length: expected {AES_GCM_NONCE_SIZE}")
    aesgcm = AESGCM(key)
    try:
        return aesgcm.decrypt(nonce, ciphertext, associated_data)
    except InvalidTag:
        raise TamperedMessageError("Authentication tag mismatch: data tampered or corrupted!")
    except Exception as e:
        raise DecryptionError(f"Binary decryption error: {e}")

def compute_file_sha256(file_path: str) -> str:
    """
    Calculate the SHA-256 checksum of a file in chunks to handle large files efficiently.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(FILE_CHUNK_SIZE)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()

def compute_bytes_sha256(data: bytes) -> str:
    """Compute SHA-256 hex digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()
