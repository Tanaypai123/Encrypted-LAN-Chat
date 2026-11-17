"""
Unit Tests for Communication Protocol and Packet Framing.
Tests length-prefixed packet serialization, validation, and malformed frame rejection.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import pytest
import struct
import json

from app.protocol import (
    ProtocolMessageType,
    create_message,
    pack_message,
    unpack_message,
    ProtocolError
)

def test_create_and_pack_message():
    msg = create_message(
        msg_type=ProtocolMessageType.CHAT_MESSAGE,
        sender="alice",
        receiver="bob",
        payload={"text": "Hello, Bob!"}
    )

    packet = pack_message(msg)
    # Check 4-byte big-endian header
    header = packet[:4]
    payload_bytes = packet[4:]
    (length,) = struct.unpack("!I", header)
    assert length == len(payload_bytes)

    # Unpack and verify structure
    unpacked = unpack_message(payload_bytes)
    assert unpacked["type"] == ProtocolMessageType.CHAT_MESSAGE
    assert unpacked["sender"] == "alice"
    assert unpacked["receiver"] == "bob"
    assert unpacked["payload"]["text"] == "Hello, Bob!"

def test_unpack_malformed_json():
    corrupted_bytes = b'{"type": "CHAT", "sender": incomplete...'
    with pytest.raises(ProtocolError):
        unpack_message(corrupted_bytes)

def test_unpack_missing_required_fields():
    incomplete_dict = {"type": "CHAT", "sender": "alice"}
    raw_bytes = json.dumps(incomplete_dict).encode("utf-8")
    with pytest.raises(ProtocolError) as exc:
        unpack_message(raw_bytes)
    assert "Missing required protocol fields" in str(exc.value)
