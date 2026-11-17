"""
Integration Tests for End-to-End Encrypted Real-Time Messaging.
Tests peer key agreement handshake, encrypted packet routing through server,
decryption, and SQLite persistence.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import time
import socket
import pytest
import tempfile
from pathlib import Path

from app.database import DatabaseManager
from app.server import LANServer
from app.client import LANClient
from app.key_exchange import KeyExchangeManager
from app.messaging import MessagingService

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

@pytest.fixture
def test_system():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_msg.db"
        server_db = DatabaseManager(db_path)
        port = find_free_port()
        server = LANServer(host="127.0.0.1", port=port, db_manager=server_db)
        server.start()
        time.sleep(0.1)

        # Alice setup
        alice_db = DatabaseManager(Path(tmp_dir) / "alice.db")
        alice_client = LANClient()
        alice_km = KeyExchangeManager()
        alice_msg_svc = MessagingService(client=alice_client, key_mgr=alice_km, db_mgr=alice_db)
        alice_client.on_message_received = alice_msg_svc.handle_protocol_message

        # Bob setup
        bob_db = DatabaseManager(Path(tmp_dir) / "bob.db")
        bob_client = LANClient()
        bob_km = KeyExchangeManager()
        bob_msg_svc = MessagingService(client=bob_client, key_mgr=bob_km, db_mgr=bob_db)
        bob_client.on_message_received = bob_msg_svc.handle_protocol_message

        yield {
            "server": server,
            "port": port,
            "alice": {"client": alice_client, "msg": alice_msg_svc, "km": alice_km, "db": alice_db},
            "bob": {"client": bob_client, "msg": bob_msg_svc, "km": bob_km, "db": bob_db}
        }

        alice_client.disconnect()
        bob_client.disconnect()
        server.stop()

def test_e2e_encrypted_chat_between_peers(test_system):
    port = test_system["port"]
    a = test_system["alice"]
    b = test_system["bob"]

    # Register & Login
    a["client"].register("127.0.0.1", port, "alice", "PassWord123")
    b["client"].register("127.0.0.1", port, "bob", "PassWord123")

    a["client"].login("127.0.0.1", port, "alice", "PassWord123")
    b["client"].login("127.0.0.1", port, "bob", "PassWord123")
    time.sleep(0.1)

    bob_received_messages = []
    alice_received_messages = []

    b["msg"].on_message_received = lambda s, text, ts, mid: bob_received_messages.append((s, text))
    a["msg"].on_message_received = lambda s, text, ts, mid: alice_received_messages.append((s, text))

    # Alice sends message to Bob (triggers auto X25519 key exchange first)
    a["msg"].send_chat_message("bob", "Hello Bob! This message is E2E encrypted.")

    # Allow key exchange and message dispatch to complete
    time.sleep(0.4)

    assert len(bob_received_messages) == 1
    sender, text = bob_received_messages[0]
    assert sender == "alice"
    assert text == "Hello Bob! This message is E2E encrypted."

    # Both must now share the exact same symmetric session key
    alice_key = a["km"].get_session_key("bob")
    bob_key = b["km"].get_session_key("alice")
    assert alice_key is not None
    assert alice_key == bob_key

    # Bob replies to Alice
    b["msg"].send_chat_message("alice", "Hi Alice! Received securely.")
    time.sleep(0.2)

    assert len(alice_received_messages) == 1
    s_reply, t_reply = alice_received_messages[0]
    assert s_reply == "bob"
    assert t_reply == "Hi Alice! Received securely."

    # Check local SQLite history for Alice
    alice_history = a["msg"].get_chat_history("bob")
    assert len(alice_history) == 2
    contents = [m["message_content"] for m in alice_history]
    assert "Hello Bob! This message is E2E encrypted." in contents
    assert "Hi Alice! Received securely." in contents
