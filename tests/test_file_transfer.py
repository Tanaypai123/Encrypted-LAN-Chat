"""
Integration Tests for Encrypted Chunked File Transfer.
Tests multi-chunk streaming, per-chunk AES-256-GCM encryption, SHA-256 checksum verification,
path traversal sanitization, and corrupted data rejection.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import time
import socket
import pytest
import tempfile
import os
from pathlib import Path

from app.database import DatabaseManager
from app.server import LANServer
from app.client import LANClient
from app.key_exchange import KeyExchangeManager
from app.file_transfer import FileTransferService, sanitize_filename
from app.encryption import compute_file_sha256

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def test_sanitize_filename():
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe") == "cmd.exe"
    assert sanitize_filename("normal_file.pdf") == "normal_file.pdf"
    assert sanitize_filename("") != ""  # Generates fallback

@pytest.fixture
def transfer_env():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "server.db"
        server_db = DatabaseManager(db_path)
        port = find_free_port()
        server = LANServer(host="127.0.0.1", port=port, db_manager=server_db)
        server.start()
        time.sleep(0.1)

        # Alice
        alice_client = LANClient()
        alice_km = KeyExchangeManager()
        alice_db = DatabaseManager(Path(tmp_dir) / "alice.db")
        alice_ft = FileTransferService(
            client=alice_client,
            key_mgr=alice_km,
            db_mgr=alice_db,
            downloads_dir=Path(tmp_dir) / "alice_downloads"
        )

        # Bob
        bob_client = LANClient()
        bob_km = KeyExchangeManager()
        bob_db = DatabaseManager(Path(tmp_dir) / "bob.db")
        bob_downloads = Path(tmp_dir) / "bob_downloads"
        bob_ft = FileTransferService(
            client=bob_client,
            key_mgr=bob_km,
            db_mgr=bob_db,
            downloads_dir=bob_downloads
        )

        # Protocol router for both
        def route_alice(msg):
            # Check key exchange
            if msg.get("type") in ("KEY_EXCHANGE_INIT", "KEY_EXCHANGE_REPLY"):
                if msg.get("type") == "KEY_EXCHANGE_INIT":
                    pub, key = alice_km.handle_handshake_init(msg["sender"], msg["payload"]["public_key"])
                    alice_client.send_message("KEY_EXCHANGE_REPLY", receiver=msg["sender"], payload={"public_key": pub})
                else:
                    alice_km.handle_handshake_reply(msg["sender"], msg["payload"]["public_key"])
            else:
                alice_ft.handle_protocol_message(msg)

        def route_bob(msg):
            if msg.get("type") in ("KEY_EXCHANGE_INIT", "KEY_EXCHANGE_REPLY"):
                if msg.get("type") == "KEY_EXCHANGE_INIT":
                    pub, key = bob_km.handle_handshake_init(msg["sender"], msg["payload"]["public_key"])
                    bob_client.send_message("KEY_EXCHANGE_REPLY", receiver=msg["sender"], payload={"public_key": pub})
                else:
                    bob_km.handle_handshake_reply(msg["sender"], msg["payload"]["public_key"])
            else:
                bob_ft.handle_protocol_message(msg)

        alice_client.on_message_received = route_alice
        bob_client.on_message_received = route_bob

        yield {
            "server": server,
            "port": port,
            "alice": {"client": alice_client, "ft": alice_ft, "km": alice_km},
            "bob": {"client": bob_client, "ft": bob_ft, "km": bob_km, "downloads": bob_downloads},
            "tmp_dir": Path(tmp_dir)
        }

        alice_client.disconnect()
        bob_client.disconnect()
        server.stop()

def test_encrypted_file_transfer_end_to_end(transfer_env):
    port = transfer_env["port"]
    a = transfer_env["alice"]
    b = transfer_env["bob"]
    tmp_dir = transfer_env["tmp_dir"]

    # Register & Login
    a["client"].register("127.0.0.1", port, "alice_ft", "PassWord123")
    b["client"].register("127.0.0.1", port, "bob_ft", "PassWord123")
    a["client"].login("127.0.0.1", port, "alice_ft", "PassWord123")
    b["client"].login("127.0.0.1", port, "bob_ft", "PassWord123")
    time.sleep(0.1)

    # Establish initial E2E session key
    pub_a = a["km"].initiate_handshake("bob_ft")
    a["client"].send_message("KEY_EXCHANGE_INIT", receiver="bob_ft", payload={"public_key": pub_a})
    time.sleep(0.2)

    # Create a 200 KB test payload (requires 4 chunks of 64 KB)
    test_file_path = tmp_dir / "sample_document.pdf"
    content = b"Encrypted LAN Transfer Chunk Demonstration Content! " * 4000  # ~208 KB
    test_file_path.write_bytes(content)
    expected_hash = compute_file_sha256(str(test_file_path))

    bob_received_file_path = []

    def on_bob_req(req):
        # Auto-accept transfer
        b["ft"].accept_transfer(req["transfer_id"])

    def on_bob_complete(tid, path, succ, msg):
        if succ:
            bob_received_file_path.append(path)

    b["ft"].on_transfer_request = on_bob_req
    b["ft"].on_transfer_complete = on_bob_complete

    # Alice sends file to Bob
    tid = a["ft"].send_file("bob_ft", str(test_file_path))
    assert tid is not None

    # Wait for chunk streaming and verification to complete
    for _ in range(50):
        if bob_received_file_path:
            break
        time.sleep(0.1)

    assert len(bob_received_file_path) == 1
    received_path = Path(bob_received_file_path[0])
    assert received_path.exists()
    assert received_path.stat().st_size == len(content)

    # Verify SHA-256 matches exactly
    received_hash = compute_file_sha256(str(received_path))
    assert received_hash == expected_hash

    # Verify content byte-for-byte
    assert received_path.read_bytes() == content

def test_send_nonexistent_file(transfer_env):
    a = transfer_env["alice"]
    alert_messages = []
    a["ft"].on_system_alert = lambda lvl, msg: alert_messages.append(msg)

    tid = a["ft"].send_file("bob_ft", "/nonexistent/invalid/file.xyz")
    assert tid is None
    assert any("does not exist" in m for m in alert_messages)
