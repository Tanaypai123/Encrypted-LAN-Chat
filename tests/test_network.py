"""
Integration Tests for TCP Server and Client Networking.
Tests server lifecycle, concurrent client connections, presence broadcast, and disconnection handling.
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

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

@pytest.fixture
def test_env():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_net.db"
        db = DatabaseManager(db_path)
        port = find_free_port()
        server = LANServer(host="127.0.0.1", port=port, db_manager=db)
        server.start()
        time.sleep(0.1)

        yield {"server": server, "db": db, "port": port}

        server.stop()

def test_server_startup_and_shutdown(test_env):
    server = test_env["server"]
    assert server.is_running is True
    server.stop()
    assert server.is_running is False

def test_client_registration_and_login(test_env):
    port = test_env["port"]
    client = LANClient()

    # Register user1
    reg_res = client.register("127.0.0.1", port, "netuser1", "PassWord123")
    assert reg_res.get("success") is True

    # Login user1
    login_res = client.login("127.0.0.1", port, "netuser1", "PassWord123")
    assert login_res.get("success") is True
    assert client.is_connected is True
    assert client.current_user == "netuser1"

    client.disconnect()
    assert client.is_connected is False

def test_two_concurrent_clients_and_presence(test_env):
    port = test_env["port"]
    client_a = LANClient()
    client_b = LANClient()

    # Register both
    client_a.register("127.0.0.1", port, "alice_net", "PassWord123")
    client_b.register("127.0.0.1", port, "bob_net", "PassWord123")

    user_list_b_received = []

    def on_users_b(users):
        user_list_b_received.extend(users)

    client_b.on_user_list_updated = on_users_b

    # Login Alice
    client_a.login("127.0.0.1", port, "alice_net", "PassWord123")

    # Login Bob
    client_b.login("127.0.0.1", port, "bob_net", "PassWord123")

    # Allow broadcast loop to propagate
    time.sleep(0.3)

    online_users = test_env["server"].get_online_users()
    usernames = [u["username"] for u in online_users]
    assert "alice_net" in usernames
    assert "bob_net" in usernames

    client_a.disconnect()
    client_b.disconnect()

def test_multiple_concurrent_clients(test_env):
    port = test_env["port"]
    clients = []
    num_clients = 5

    try:
        for i in range(num_clients):
            c = LANClient()
            uname = f"client_{i}"
            c.register("127.0.0.1", port, uname, "SecurePass123")
            c.login("127.0.0.1", port, uname, "SecurePass123")
            clients.append(c)

        time.sleep(0.3)
        online = test_env["server"].get_online_users()
        assert len(online) == num_clients
    finally:
        for c in clients:
            c.disconnect()
