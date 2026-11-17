"""
Multi-threaded LAN TCP Server.
Handles client authentication, concurrent connection management, routing of
end-to-end encrypted packets, presence tracking, and graceful shutdowns.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import socket
import threading
import time
import logging
from typing import Dict, Any, Optional, Callable, List

from config import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    get_local_ip,
    SOCKET_BUFFER_SIZE
)
from app.protocol import (
    ProtocolMessageType,
    create_message,
    send_framed_message,
    recv_framed_message,
    ProtocolError
)
from app.database import DatabaseManager
from app.authentication import AuthenticationManager, AuthenticationError, RateLimitExceededError

logger = logging.getLogger("LANServer")

class LANServer:
    """Thread-safe TCP Server managing multiple simultaneous LAN client connections."""

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        db_manager: Optional[DatabaseManager] = None,
        on_log: Optional[Callable[[str], None]] = None,
        on_client_change: Optional[Callable[[List[Dict[str, Any]]], None]] = None
    ):
        self.host = host
        self.port = port
        self.db = db_manager or DatabaseManager.get_instance()
        self.auth_manager = AuthenticationManager(self.db)
        self.on_log = on_log or (lambda msg: None)
        self.on_client_change = on_client_change or (lambda clients: None)

        self._server_socket: Optional[socket.socket] = None
        self._is_running = False
        self._lock = threading.RLock()

        # Connected clients: {username: {"socket": sock, "address": addr, "connected_at": float, "status": "online"}}
        self._connected_clients: Dict[str, Dict[str, Any]] = {}
        # Reverse lookup: {socket: username}
        self._socket_to_username: Dict[socket.socket, str] = {}

    @property
    def is_running(self) -> bool:
        return self._is_running

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        log_line = f"[{timestamp}] [Server] {message}"
        logger.info(log_line)
        try:
            self.on_log(log_line)
        except Exception:
            pass

    def start(self) -> bool:
        """Start listening for incoming TCP connections."""
        with self._lock:
            if self._is_running:
                return True

            try:
                self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._server_socket.bind((self.host, self.port))
                self._server_socket.listen(128)
                self._is_running = True

                lan_ip = get_local_ip()
                self.log(f"Server started on {self.host}:{self.port} (LAN IP: {lan_ip})")

                # Accept loop thread
                accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
                accept_thread.start()
                return True
            except Exception as e:
                self.log(f"Error starting server: {e}")
                self._is_running = False
                if self._server_socket:
                    try:
                        self._server_socket.close()
                    except Exception:
                        pass
                    self._server_socket = None
                return False

    def stop(self):
        """Stop server and disconnect all clients cleanly."""
        with self._lock:
            if not self._is_running:
                return
            self._is_running = False

            self.log("Stopping server and closing client connections...")

            # Close all active client sockets
            for username, data in list(self._connected_clients.items()):
                try:
                    sock = data["socket"]
                    send_framed_message(sock, create_message(
                        ProtocolMessageType.ERROR,
                        sender="SERVER",
                        receiver=username,
                        payload={"error": "Server is shutting down."}
                    ))
                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()
                except Exception:
                    pass

            self._connected_clients.clear()
            self._socket_to_username.clear()

            if self._server_socket:
                try:
                    self._server_socket.close()
                except Exception:
                    pass
                self._server_socket = None

            self.log("Server stopped successfully.")
            self._notify_client_change()

    def _accept_loop(self):
        """Continuously accept incoming client connections."""
        while self._is_running and self._server_socket:
            try:
                self._server_socket.settimeout(0.5)
                client_sock, client_addr = self._server_socket.accept()
                client_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.log(f"Connection attempt from {client_addr[0]}:{client_addr[1]}")

                # Client handler thread
                t = threading.Thread(
                    target=self._handle_client_connection,
                    args=(client_sock, client_addr),
                    daemon=True
                )
                t.start()
            except socket.timeout:
                continue
            except (socket.error, OSError):
                # Socket closed during shutdown
                break
            except Exception as e:
                self.log(f"Accept loop error: {e}")

    def _handle_client_connection(self, client_sock: socket.socket, client_addr: tuple):
        """Authenticate and manage a connected client."""
        username: Optional[str] = None
        try:
            client_sock.settimeout(15.0)  # 15 seconds to complete authentication
            auth_msg = recv_framed_message(client_sock)

            if auth_msg.get("type") != ProtocolMessageType.AUTH_REQUEST:
                send_framed_message(client_sock, create_message(
                    ProtocolMessageType.AUTH_RESPONSE,
                    sender="SERVER",
                    receiver="ANONYMOUS",
                    payload={"success": False, "error": "First message must be AUTH_REQUEST."}
                ))
                client_sock.close()
                return

            payload = auth_msg.get("payload", {})
            req_username = payload.get("username", "").strip()
            password = payload.get("password", "")
            action = payload.get("action", "login")  # 'login' or 'register'

            if action == "register":
                try:
                    reg_res = self.auth_manager.register(req_username, password)
                    send_framed_message(client_sock, create_message(
                        ProtocolMessageType.AUTH_RESPONSE,
                        sender="SERVER",
                        receiver=req_username,
                        payload={"success": True, "message": reg_res["message"], "action": "register"}
                    ))
                    client_sock.close()
                    self.log(f"User '{req_username}' registered from {client_addr[0]}")
                    return
                except Exception as e:
                    send_framed_message(client_sock, create_message(
                        ProtocolMessageType.AUTH_RESPONSE,
                        sender="SERVER",
                        receiver=req_username,
                        payload={"success": False, "error": str(e), "action": "register"}
                    ))
                    client_sock.close()
                    return

            # Login verification
            try:
                session = self.auth_manager.login(req_username, password, lan_ip=client_addr[0])
            except (AuthenticationError, RateLimitExceededError) as e:
                send_framed_message(client_sock, create_message(
                    ProtocolMessageType.AUTH_RESPONSE,
                    sender="SERVER",
                    receiver=req_username,
                    payload={"success": False, "error": str(e), "action": "login"}
                ))
                client_sock.close()
                self.log(f"Authentication failed for '{req_username}' from {client_addr[0]}: {e}")
                return

            # Prevent duplicate active logins
            with self._lock:
                if req_username in self._connected_clients:
                    send_framed_message(client_sock, create_message(
                        ProtocolMessageType.AUTH_RESPONSE,
                        sender="SERVER",
                        receiver=req_username,
                        payload={"success": False, "error": f"User '{req_username}' is already logged in.", "action": "login"}
                    ))
                    client_sock.close()
                    return

                username = req_username
                self._connected_clients[username] = {
                    "socket": client_sock,
                    "address": client_addr,
                    "connected_at": time.time(),
                    "status": "online",
                    "session_token": session.session_token
                }
                self._socket_to_username[client_sock] = username

            # Authentication successful
            send_framed_message(client_sock, create_message(
                ProtocolMessageType.AUTH_RESPONSE,
                sender="SERVER",
                receiver=username,
                payload={
                    "success": True,
                    "message": "Authenticated successfully.",
                    "session_token": session.session_token,
                    "username": username,
                    "server_time": time.time()
                }
            ))
            self.log(f"User '{username}' successfully connected from {client_addr[0]}:{client_addr[1]}")

            # Notify all clients of new user presence
            self._broadcast_user_list()
            self._notify_client_change()

            # Set infinite or long timeout for regular session loop
            client_sock.settimeout(None)

            # Communication loop
            while self._is_running:
                msg = recv_framed_message(client_sock)
                self._dispatch_client_message(username, msg)

        except (ConnectionResetError, BrokenPipeError, EOFError):
            self.log(f"Client disconnected: {username or client_addr[0]}")
        except Exception as e:
            self.log(f"Client '{username or client_addr[0]}' connection error: {e}")
        finally:
            self._cleanup_client(client_sock, username)

    def _dispatch_client_message(self, sender: str, msg: Dict[str, Any]):
        """Route client message based on recipient."""
        msg_type = msg.get("type")
        receiver = msg.get("receiver")

        if receiver == "SERVER":
            self._handle_server_request(sender, msg)
        elif receiver == "BROADCAST":
            self._broadcast_message(msg, exclude_user=sender)
        else:
            # Route directly to specific recipient
            with self._lock:
                recipient_data = self._connected_clients.get(receiver)

            if recipient_data:
                try:
                    send_framed_message(recipient_data["socket"], msg)
                except Exception as e:
                    self.log(f"Failed to route message from '{sender}' to '{receiver}': {e}")
            else:
                # Recipient not online
                with self._lock:
                    sender_data = self._connected_clients.get(sender)
                if sender_data:
                    try:
                        send_framed_message(sender_data["socket"], create_message(
                            ProtocolMessageType.ERROR,
                            sender="SERVER",
                            receiver=sender,
                            payload={"error": f"Recipient '{receiver}' is currently offline."}
                        ))
                    except Exception:
                        pass

    def _handle_server_request(self, sender: str, msg: Dict[str, Any]):
        """Process messages targeted at the server itself."""
        msg_type = msg.get("type")

        if msg_type == ProtocolMessageType.USER_LIST_REQUEST:
            self._send_user_list_to(sender)
        elif msg_type == ProtocolMessageType.HEARTBEAT_PING:
            with self._lock:
                client_data = self._connected_clients.get(sender)
            if client_data:
                try:
                    send_framed_message(client_data["socket"], create_message(
                        ProtocolMessageType.HEARTBEAT_PONG,
                        sender="SERVER",
                        receiver=sender,
                        payload={"timestamp": time.time()}
                    ))
                except Exception:
                    pass
        elif msg_type == ProtocolMessageType.USER_STATUS_CHANGE:
            new_status = msg.get("payload", {}).get("status", "online")
            with self._lock:
                if sender in self._connected_clients:
                    self._connected_clients[sender]["status"] = new_status
            self._broadcast_user_list()
            self._notify_client_change()

    def _cleanup_client(self, client_sock: socket.socket, username: Optional[str]):
        """Remove client from active registry and notify other peers."""
        with self._lock:
            if username and username in self._connected_clients:
                del self._connected_clients[username]
            if client_sock in self._socket_to_username:
                del self._socket_to_username[client_sock]

        try:
            client_sock.close()
        except Exception:
            pass

        if username:
            self.log(f"Cleaned up session for user '{username}'.")
            self._broadcast_user_list()
            self._notify_client_change()

    def get_online_users(self) -> List[Dict[str, Any]]:
        """Return list of currently connected user info."""
        with self._lock:
            user_list = []
            for u, data in self._connected_clients.items():
                user_list.append({
                    "username": u,
                    "ip": data["address"][0],
                    "port": data["address"][1],
                    "status": data.get("status", "online"),
                    "connected_at": data.get("connected_at")
                })
            return user_list

    def _send_user_list_to(self, username: str):
        """Send online user list to a specific client."""
        with self._lock:
            client_data = self._connected_clients.get(username)
        if not client_data:
            return

        users = self.get_online_users()
        try:
            send_framed_message(client_data["socket"], create_message(
                ProtocolMessageType.USER_LIST_UPDATE,
                sender="SERVER",
                receiver=username,
                payload={"users": users}
            ))
        except Exception as e:
            self.log(f"Failed to send user list to '{username}': {e}")

    def _broadcast_user_list(self):
        """Broadcast updated online users list to all connected clients."""
        users = self.get_online_users()
        msg = create_message(
            ProtocolMessageType.USER_LIST_UPDATE,
            sender="SERVER",
            receiver="BROADCAST",
            payload={"users": users}
        )
        self._broadcast_message(msg)

    def _broadcast_message(self, msg: Dict[str, Any], exclude_user: Optional[str] = None):
        """Send a message to all connected clients except exclude_user."""
        with self._lock:
            targets = list(self._connected_clients.items())

        for username, data in targets:
            if exclude_user and username == exclude_user:
                continue
            try:
                send_framed_message(data["socket"], msg)
            except Exception:
                pass

    def _notify_client_change(self):
        """Notify GUI callback of online client changes."""
        try:
            self.on_client_change(self.get_online_users())
        except Exception:
            pass
