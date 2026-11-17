"""
TCP Client Module for LAN Communication.
Maintains persistent connection to the server, runs background listener thread,
dispatches network protocol events, and handles automatic heartbeats.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import socket
import threading
import time
import logging
from typing import Dict, Any, Optional, Callable, List

from config import (
    SOCKET_BUFFER_SIZE,
    HEARTBEAT_INTERVAL
)
from app.protocol import (
    ProtocolMessageType,
    create_message,
    send_framed_message,
    recv_framed_message,
    ProtocolError
)

logger = logging.getLogger("LANClient")

class LANClient:
    """Multi-threaded TCP client for communicating with the LAN server."""

    def __init__(
        self,
        on_message_received: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_user_list_updated: Optional[Callable[[List[Dict[str, Any]]], None]] = None,
        on_connection_state_changed: Optional[Callable[[bool, str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ):
        self.on_message_received = on_message_received or (lambda msg: None)
        self.on_user_list_updated = on_user_list_updated or (lambda users: None)
        self.on_connection_state_changed = on_connection_state_changed or (lambda state, reason: None)
        self.on_error = on_error or (lambda err: None)

        self._socket: Optional[socket.socket] = None
        self._is_connected = False
        self._current_user: Optional[str] = None
        self._session_token: Optional[str] = None
        self._server_host: Optional[str] = None
        self._server_port: Optional[int] = None

        self._lock = threading.Lock()
        self._listener_thread: Optional[threading.Thread] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def current_user(self) -> Optional[str]:
        return self._current_user

    @property
    def session_token(self) -> Optional[str]:
        return self._session_token

    def connect(self, host: str, port: int) -> bool:
        """Establish basic TCP socket connection to server."""
        with self._lock:
            if self._is_connected:
                return True

            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self._socket.settimeout(5.0)
                self._socket.connect((host, port))
                self._server_host = host
                self._server_port = port
                return True
            except Exception as e:
                self._socket = None
                raise ConnectionError(f"Cannot connect to server at {host}:{port}: {e}")

    def register(self, host: str, port: int, username: str, password: str) -> Dict[str, Any]:
        """Register a new user account with the server."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(10.0)
            sock.connect((host, port))
            auth_msg = create_message(
                ProtocolMessageType.AUTH_REQUEST,
                sender=username,
                receiver="SERVER",
                payload={"username": username, "password": password, "action": "register"}
            )
            send_framed_message(sock, auth_msg)
            response = recv_framed_message(sock)
            payload = response.get("payload", {})
            return payload
        finally:
            try:
                sock.close()
            except Exception:
                pass

    def login(self, host: str, port: int, username: str, password: str) -> Dict[str, Any]:
        """Authenticate with the server and start background message listener."""
        self.connect(host, port)

        auth_msg = create_message(
            ProtocolMessageType.AUTH_REQUEST,
            sender=username,
            receiver="SERVER",
            payload={"username": username, "password": password, "action": "login"}
        )
        send_framed_message(self._socket, auth_msg)

        # Wait for authentication response
        self._socket.settimeout(10.0)
        response = recv_framed_message(self._socket)
        payload = response.get("payload", {})

        if not payload.get("success", False):
            self.disconnect("Authentication failed")
            raise ConnectionError(payload.get("error", "Login rejected by server."))

        # Authentication succeeded
        with self._lock:
            self._is_connected = True
            self._current_user = username
            self._session_token = payload.get("session_token")
            self._socket.settimeout(None)  # Infinite timeout for receiver loop
            self._stop_event.clear()

        # Start background threads
        self._listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listener_thread.start()

        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

        self.on_connection_state_changed(True, f"Connected to {host}:{port}")

        # Request user list
        self.send_message(
            ProtocolMessageType.USER_LIST_REQUEST,
            receiver="SERVER",
            payload={}
        )

        return payload

    def send_message(self, msg_type: str, receiver: str, payload: Optional[Dict[str, Any]] = None) -> bool:
        """Send a framed protocol message to a peer or server."""
        if not self._is_connected or not self._socket:
            return False

        message = create_message(
            msg_type=msg_type,
            sender=self._current_user or "ANONYMOUS",
            receiver=receiver,
            payload=payload or {}
        )

        with self._lock:
            try:
                send_framed_message(self._socket, message)
                return True
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                self.disconnect(f"Send failed: {e}")
                return False

    def _listen_loop(self):
        """Continuously receive framed protocol packets from server."""
        while not self._stop_event.is_set() and self._socket:
            try:
                msg = recv_framed_message(self._socket)
                self._dispatch_incoming_message(msg)
            except (ConnectionResetError, BrokenPipeError, EOFError):
                if not self._stop_event.is_set():
                    self.disconnect("Connection dropped by server.")
                break
            except Exception as e:
                if not self._stop_event.is_set():
                    logger.error(f"Error in client listener loop: {e}")
                    self.disconnect(f"Protocol error: {e}")
                break

    def _dispatch_incoming_message(self, msg: Dict[str, Any]):
        """Dispatch incoming messages to specific callbacks."""
        msg_type = msg.get("type")

        if msg_type == ProtocolMessageType.USER_LIST_UPDATE:
            users = msg.get("payload", {}).get("users", [])
            self.on_user_list_updated(users)
        elif msg_type == ProtocolMessageType.HEARTBEAT_PONG:
            # Heartbeat acknowledged
            pass
        elif msg_type == ProtocolMessageType.ERROR:
            err = msg.get("payload", {}).get("error", "Unknown server error")
            self.on_error(err)
        else:
            # Chat messages, key exchanges, file transfers
            self.on_message_received(msg)

    def _heartbeat_loop(self):
        """Send periodic heartbeat to server to keep connection alive."""
        while not self._stop_event.is_set() and self._is_connected:
            self._stop_event.wait(HEARTBEAT_INTERVAL)
            if self._stop_event.is_set():
                break
            try:
                self.send_message(ProtocolMessageType.HEARTBEAT_PING, receiver="SERVER", payload={})
            except Exception:
                break

    def disconnect(self, reason: str = "User logged out"):
        """Disconnect cleanly from server."""
        with self._lock:
            if not self._is_connected and not self._socket:
                return

            self._is_connected = False
            self._stop_event.set()

            if self._socket:
                try:
                    # Notify server
                    send_framed_message(self._socket, create_message(
                        ProtocolMessageType.LOGOUT_NOTIFY,
                        sender=self._current_user or "ANONYMOUS",
                        receiver="SERVER",
                        payload={"reason": reason}
                    ))
                except Exception:
                    pass

                try:
                    self._socket.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass

                try:
                    self._socket.close()
                except Exception:
                    pass
                self._socket = None

            self._current_user = None
            self._session_token = None

        self.on_connection_state_changed(False, reason)
