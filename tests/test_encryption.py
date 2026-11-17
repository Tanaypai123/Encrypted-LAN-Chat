"""
Unit Tests for Cryptographic Subsystem.
Tests AES-256-GCM authenticated encryption, unique nonces, tampered message rejection,
and SHA-256 integrity calculation.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import pytest
import base64
import tempfile
from pathlib import Path

from app.encryption import (
    generate_symmetric_key,
    encrypt_message,
    decrypt_message,
    encrypt_bytes,
    decrypt_bytes,
    compute_file_sha256,
    compute_bytes_sha256,
    TamperedMessageError,
    DecryptionError
)

def test_aes_gcm_encrypt_decrypt():
    key = generate_symmetric_key()
    original_text = "Confidential LAN message from Alice: Meet at 4 PM."

    encrypted = encrypt_message(original_text, key)
    assert "ciphertext" in encrypted
    assert "nonce" in encrypted

    decrypted = decrypt_message(encrypted, key)
    assert decrypted == original_text

def test_aes_gcm_unique_nonces():
    key = generate_symmetric_key()
    msg = "Identical message content"

    enc1 = encrypt_message(msg, key)
    enc2 = encrypt_message(msg, key)

    # Nonces must NEVER be reused
    assert enc1["nonce"] != enc2["nonce"]
    # Ciphertext must differ because nonces differ
    assert enc1["ciphertext"] != enc2["ciphertext"]

def test_tampered_ciphertext_detection():
    key = generate_symmetric_key()
    encrypted = encrypt_message("Top secret payload", key)

    raw_cipher = bytearray(base64.b64decode(encrypted["ciphertext"]))
    # Flip one byte in the ciphertext payload
    raw_cipher[5] ^= 0xFF
    tampered_payload = {
        "ciphertext": base64.b64encode(bytes(raw_cipher)).decode("utf-8"),
        "nonce": encrypted["nonce"]
    }

    with pytest.raises(TamperedMessageError):
        decrypt_message(tampered_payload, key)

def test_tampered_nonce_detection():
    key = generate_symmetric_key()
    encrypted = encrypt_message("Top secret payload", key)

    raw_nonce = bytearray(base64.b64decode(encrypted["nonce"]))
    raw_nonce[0] ^= 0x01
    tampered_payload = {
        "ciphertext": encrypted["ciphertext"],
        "nonce": base64.b64encode(bytes(raw_nonce)).decode("utf-8")
    }

    with pytest.raises(TamperedMessageError):
        decrypt_message(tampered_payload, key)

def test_wrong_key_fails_decryption():
    key1 = generate_symmetric_key()
    key2 = generate_symmetric_key()

    encrypted = encrypt_message("Secret data", key1)
    with pytest.raises(TamperedMessageError):
        decrypt_message(encrypted, key2)

def test_binary_chunk_encryption_decryption():
    key = generate_symmetric_key()
    raw_data = b"\x00\xFF\xAA\x55" * 1024  # 4 KB raw bytes

    ciphertext, nonce = encrypt_bytes(raw_data, key)
    assert len(nonce) == 12

    decrypted = decrypt_bytes(ciphertext, nonce, key)
    assert decrypted == raw_data

def test_file_sha256_computation():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"Reliable file content for checksum verification.")
        temp_path = f.name

    try:
        calculated_hash = compute_file_sha256(temp_path)
        expected_hash = compute_bytes_sha256(b"Reliable file content for checksum verification.")
        assert calculated_hash == expected_hash
    finally:
        Path(temp_path).unlink()
