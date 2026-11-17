"""
Unit Tests for Key Exchange Subsystem.
Tests Curve25519 (X25519) Diffie-Hellman ephemeral key exchange and HKDF session key derivation.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import pytest
import base64

from app.key_exchange import KeyExchangeSession, KeyExchangeManager

def test_x25519_key_exchange_derivation():
    # Alice generates session
    alice_session = KeyExchangeSession()
    alice_pub_bytes = alice_session.get_public_key_bytes()
    assert len(alice_pub_bytes) == 32

    # Bob generates session
    bob_session = KeyExchangeSession()
    bob_pub_bytes = bob_session.get_public_key_bytes()
    assert len(bob_pub_bytes) == 32

    # Both derive session key
    alice_derived_key = alice_session.derive_session_key(bob_pub_bytes)
    bob_derived_key = bob_session.derive_session_key(alice_pub_bytes)

    # Derived symmetric keys must match identically!
    assert len(alice_derived_key) == 32
    assert alice_derived_key == bob_derived_key

def test_key_exchange_manager_handshake():
    alice_mgr = KeyExchangeManager()
    bob_mgr = KeyExchangeManager()

    # Alice initiates handshake with Bob
    alice_pub_b64 = alice_mgr.initiate_handshake("bob")
    assert alice_mgr.has_session_key("bob") is False

    # Bob receives Alice's handshake and replies
    bob_pub_b64, bob_key = bob_mgr.handle_handshake_init("alice", alice_pub_b64)
    assert bob_mgr.has_session_key("alice") is True

    # Alice receives Bob's reply and finalizes
    alice_key = alice_mgr.handle_handshake_reply("bob", bob_pub_b64)
    assert alice_mgr.has_session_key("bob") is True

    # Session keys must match!
    assert alice_key == bob_key
    assert alice_mgr.get_session_key("bob") == bob_mgr.get_session_key("alice")
