"""
Unified Network & Application Manager.
Acts as the central orchestrator connecting authentication, server, client,
cryptography, messaging, and file transfer services for GUI consumption.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import threading
import logging
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path

from config import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DOWNLOADS_DIR,
    get_local_ip
)
from app.database import DatabaseManager
from app.authentication import AuthenticationManager, UserSession
from app.server import LANServer
from app.client import LANClient
from app.key_exchange import KeyExchangeManager
from app.messaging import MessagingService
from app.file_transfer import FileTransferService

logger = logging.getLogger("NetworkManager")

class NetworkManager:
    """Central orchestrator for all LAN operations, security, and GUI event routing."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager.get_instance()
        self.auth = AuthenticationManager(self.db)
        self.key_mgr = KeyExchangeManager()

        # GUI Event Callback hooks
        self.on_log: Callable[[str], None] = lambda msg: None
        self.on_user_list_changed: Callable[[List[Dict[str, Any]]], None] = lambda users: None
        self.on_chat_received: Callable[[str, str, str, str], None] = lambda sender, text, ts, mid: None
        self.on_file_requested: Callable[[Dict[str, Any]], None] = lambda req: None
        self.on_file_progress: Callable[[str, float, str, int, int], None] = lambda tid, pct, st, done, tot: None
        self.on_file_complete: Callable[[str, str, bool, str], None] = lambda tid, path, succ, msg: None
        self.on_connection_changed: Callable[[bool, str], None] = lambda state, reason: None
        self.on_security_alert: Callable[[str, str], None] = lambda lvl, msg: None
        self.on_server_status_changed: Callable[[bool, str], None] = lambda running, addr: None
        self.on_server_clients_changed: Callable[[List[Dict[str, Any]]], None] = lambda clients: None

        # Underlying Subsystems
        self.server: Optional[LANServer] = None
        self.client = LANClient(
            on_message_received=self._on_client_protocol_message,
            on_user_list_updated=self._on_client_user_list,
            on_connection_state_changed=self._on_client_conn_state,
            on_error=self._on_client_error
        )

        self.messaging = MessagingService(
            client=self.client,
            key_mgr=self.key_mgr,
            db_mgr=self.db,
            on_message_received=self._on_chat_msg,
            on_system_alert=self._on_sec_alert,
            on_key_exchange_complete=self._on_key_exchange_done
        )

        self.file_transfer = FileTransferService(
            client=self.client,
            key_mgr=self.key_mgr,
            db_mgr=self.db,
            downloads_dir=DOWNLOADS_DIR,
            on_transfer_request=self._on_file_req,
            on_progress_update=self._on_file_prog,
            on_transfer_complete=self._on_file_comp,
            on_system_alert=self._on_sec_alert
        )

        self._active_connection_id: Optional[int] = None

    # --- Server Operations ---

    def start_server(self, port: int = DEFAULT_PORT) -> bool:
        """Start local TCP LAN Server."""
        if self.server and self.server.is_running:
            return True

        self.server = LANServer(
            host=DEFAULT_HOST,
            port=port,
            db_manager=self.db,
            on_log=self.on_log,
            on_client_change=self.on_server_clients_changed
        )
        started = self.server.start()
        if started:
            lan_ip = get_local_ip()
            self.on_server_status_changed(True, f"{lan_ip}:{port}")
        return started

    def stop_server(self):
        """Stop local LAN Server."""
        if self.server:
            self.server.stop()
            self.server = None
            self.on_server_status_changed(False, "Stopped")

    def is_server_running(self) -> bool:
        return self.server is not None and self.server.is_running

    # --- Client Connection & Authentication ---

    def register(self, host: str, port: int, username: str, password: str) -> Dict[str, Any]:
        """Register a new user through the network."""
        return self.client.register(host, port, username, password)

    def login(self, host: str, port: int, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user against server and start session."""
        res = self.client.login(host, port, username, password)
        self._active_connection_id = self.db.record_connection(host, port, "connected")
        return res

    def logout(self):
        """Disconnect and clear all session keys."""
        if self._active_connection_id:
            self.db.record_disconnection(self._active_connection_id)
            self._active_connection_id = None
        self.key_mgr.clear_all()
        self.client.disconnect("User logged out")

    @property
    def is_connected(self) -> bool:
        return self.client.is_connected

    @property
    def current_username(self) -> Optional[str]:
        return self.client.current_user

    # --- Messaging & Key Agreement ---

    def send_chat(self, receiver: str, text: str) -> bool:
        """Send E2E encrypted chat message."""
        return self.messaging.send_chat_message(receiver, text)

    def get_chat_history(self, peer: str) -> List[Dict[str, Any]]:
        """Retrieve conversation history with peer."""
        return self.messaging.get_chat_history(peer)

    def has_encryption_key_for(self, peer: str) -> bool:
        """Check if an active AES-256-GCM / X25519 session key exists for peer."""
        return self.key_mgr.has_session_key(peer)

    # --- File Transfer Operations ---

    def send_file(self, receiver: str, file_path: str) -> Optional[str]:
        """Send file encrypted over LAN."""
        return self.file_transfer.send_file(receiver, file_path)

    def accept_file(self, transfer_id: str, custom_download_path: Optional[str] = None) -> bool:
        """Accept an incoming file."""
        return self.file_transfer.accept_transfer(transfer_id, custom_download_path)

    def reject_file(self, transfer_id: str):
        """Reject an incoming file."""
        self.file_transfer.reject_transfer(transfer_id)

    def get_transfer_history(self) -> List[Dict[str, Any]]:
        """Retrieve file transfer history."""
        return self.file_transfer.get_transfer_history()

    # --- Internal Dispatchers ---

    def _on_client_protocol_message(self, msg: Dict[str, Any]):
        """Route incoming packet between messaging and file transfer."""
        handled = self.messaging.handle_protocol_message(msg)
        if not handled:
            self.file_transfer.handle_protocol_message(msg)

    def _on_client_user_list(self, users: List[Dict[str, Any]]):
        self.on_user_list_changed(users)

    def _on_client_conn_state(self, state: bool, reason: str):
        if not state:
            self.key_mgr.clear_all()
        self.on_connection_changed(state, reason)

    def _on_client_error(self, err: str):
        self.on_security_alert("error", err)

    def _on_chat_msg(self, sender: str, text: str, ts: str, mid: str):
        self.on_chat_received(sender, text, ts, mid)

    def _on_sec_alert(self, level: str, msg: str):
        self.on_security_alert(level, msg)

    def _on_key_exchange_done(self, peer: str):
        self.on_log(f"Secure AES-256-GCM session established with '{peer}' via X25519.")

    def _on_file_req(self, req: Dict[str, Any]):
        self.on_file_requested(req)

    def _on_file_prog(self, tid: str, pct: float, st: str, done: int, tot: int):
        self.on_file_progress(tid, pct, st, done, tot)

    def _on_file_comp(self, tid: str, path: str, succ: bool, msg: str):
        self.on_file_complete(tid, path, succ, msg)
