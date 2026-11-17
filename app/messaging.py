"""
Encrypted Messaging Subsystem.
Orchestrates end-to-end encryption, key exchange handshakes, message persistence,
replay/tamper detection, and GUI dispatching.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import uuid
import time
import logging
from typing import Dict, Any, Optional, Callable, List

from app.protocol import ProtocolMessageType
from app.encryption import (
    encrypt_message,
    decrypt_message,
    TamperedMessageError,
    DecryptionError
)
from app.key_exchange import KeyExchangeManager
from app.database import DatabaseManager

logger = logging.getLogger("MessagingService")

class MessagingService:
    """Handles end-to-end encrypted messaging, message queues, and local chat archives."""

    def __init__(
        self,
        client: Any,
        key_mgr: KeyExchangeManager,
        db_mgr: Optional[DatabaseManager] = None,
        on_message_received: Optional[Callable[[str, str, str, str], None]] = None,
        on_system_alert: Optional[Callable[[str, str], None]] = None,
        on_key_exchange_complete: Optional[Callable[[str], None]] = None
    ):
        self.client = client
        self.key_mgr = key_mgr
        self.db = db_mgr or DatabaseManager.get_instance()
        self.on_message_received = on_message_received or (lambda sender, text, ts, mid: None)
        self.on_system_alert = on_system_alert or (lambda level, msg: None)
        self.on_key_exchange_complete = on_key_exchange_complete or (lambda peer: None)

        # Pending messages waiting for key exchange completion: {peer: [message_text, ...]}
        self._pending_outgoing: Dict[str, List[str]] = {}

    def send_chat_message(self, receiver: str, text: str) -> bool:
        """
        Send an end-to-end encrypted chat message to a peer.
        If no session key exists, automatically initiates X25519 key exchange.
        """
        sender = self.client.current_user
        if not sender:
            self.on_system_alert("error", "Cannot send message: Not logged in.")
            return False

        if not self.key_mgr.has_session_key(receiver):
            # Queue message and initiate key exchange
            if receiver not in self._pending_outgoing:
                self._pending_outgoing[receiver] = []
            self._pending_outgoing[receiver].append(text)

            pub_key_b64 = self.key_mgr.initiate_handshake(receiver)
            self.client.send_message(
                ProtocolMessageType.KEY_EXCHANGE_INIT,
                receiver=receiver,
                payload={"public_key": pub_key_b64}
            )
            logger.info(f"Initiated X25519 key exchange with '{receiver}'")
            return True

        # Session key exists - encrypt and send immediately
        session_key = self.key_mgr.get_session_key(receiver)
        try:
            encrypted_payload = encrypt_message(text, session_key)
            msg_id = str(uuid.uuid4())
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            payload = {
                "ciphertext": encrypted_payload["ciphertext"],
                "nonce": encrypted_payload["nonce"],
                "local_timestamp": timestamp
            }

            success = self.client.send_message(
                ProtocolMessageType.CHAT_MESSAGE,
                receiver=receiver,
                payload=payload
            )

            if success:
                # Store message in local database
                self.db.save_message(
                    msg_id=msg_id,
                    sender=sender,
                    receiver=receiver,
                    content=text,
                    is_encrypted=True,
                    status="sent",
                    timestamp=timestamp
                )
            return success
        except Exception as e:
            logger.error(f"Failed to encrypt/send message to '{receiver}': {e}")
            self.on_system_alert("error", f"Encryption failed: {e}")
            return False

    def handle_protocol_message(self, msg: Dict[str, Any]) -> bool:
        """
        Route and handle incoming network packets related to messaging and key exchange.
        Returns True if handled.
        """
        msg_type = msg.get("type")
        sender = msg.get("sender")
        payload = msg.get("payload", {})
        msg_id = msg.get("msg_id", str(uuid.uuid4()))
        timestamp = msg.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))

        if msg_type == ProtocolMessageType.KEY_EXCHANGE_INIT:
            self._handle_key_exchange_init(sender, payload)
            return True

        elif msg_type == ProtocolMessageType.KEY_EXCHANGE_REPLY:
            self._handle_key_exchange_reply(sender, payload)
            return True

        elif msg_type == ProtocolMessageType.CHAT_MESSAGE:
            self._handle_incoming_chat(sender, payload, msg_id, timestamp)
            return True

        return False

    def _handle_key_exchange_init(self, sender: str, payload: Dict[str, Any]):
        """Respond to incoming X25519 key exchange initiation."""
        peer_pub_key = payload.get("public_key")
        if not peer_pub_key:
            return

        try:
            own_pub_b64, session_key = self.key_mgr.handle_handshake_init(sender, peer_pub_key)
            self.client.send_message(
                ProtocolMessageType.KEY_EXCHANGE_REPLY,
                receiver=sender,
                payload={"public_key": own_pub_b64}
            )
            logger.info(f"Completed X25519 key agreement with '{sender}' (responder).")
            self.on_key_exchange_complete(sender)

            # Flush any pending messages
            self._flush_pending(sender)
        except Exception as e:
            logger.error(f"Key exchange init error from '{sender}': {e}")
            self.on_system_alert("error", f"Key exchange failed with '{sender}': {e}")

    def _handle_key_exchange_reply(self, sender: str, payload: Dict[str, Any]):
        """Finalize X25519 key exchange from peer reply."""
        peer_pub_key = payload.get("public_key")
        if not peer_pub_key:
            return

        try:
            self.key_mgr.handle_handshake_reply(sender, peer_pub_key)
            logger.info(f"Completed X25519 key agreement with '{sender}' (initiator).")
            self.on_key_exchange_complete(sender)

            # Flush pending messages
            self._flush_pending(sender)
        except Exception as e:
            logger.error(f"Key exchange reply error from '{sender}': {e}")
            self.on_system_alert("error", f"Key exchange finalization failed with '{sender}': {e}")

    def _flush_pending(self, receiver: str):
        """Send all messages queued for peer while waiting for key agreement."""
        pending = self._pending_outgoing.pop(receiver, [])
        for text in pending:
            self.send_chat_message(receiver, text)

    def _handle_incoming_chat(self, sender: str, payload: Dict[str, Any], msg_id: str, timestamp: str):
        """Decrypt, verify, and persist incoming encrypted chat message."""
        session_key = self.key_mgr.get_session_key(sender)
        if not session_key:
            self.on_system_alert("error", f"Received encrypted message from '{sender}', but no session key exists.")
            return

        try:
            plaintext = decrypt_message(payload, session_key)
            current_user = self.client.current_user or ""

            # Save to SQLite database
            self.db.save_message(
                msg_id=msg_id,
                sender=sender,
                receiver=current_user,
                content=plaintext,
                is_encrypted=True,
                status="delivered",
                timestamp=payload.get("local_timestamp", timestamp)
            )

            # Notify GUI
            self.on_message_received(sender, plaintext, timestamp, msg_id)
        except TamperedMessageError as e:
            logger.critical(f"Security Alert: Tampered message from '{sender}': {e}")
            self.on_system_alert("critical", f"SECURITY WARNING: Tampered message received from '{sender}'! Verification failed.")
        except DecryptionError as e:
            logger.error(f"Decryption error from '{sender}': {e}")
            self.on_system_alert("error", f"Failed to decrypt message from '{sender}': {e}")

    def get_chat_history(self, peer: str, limit: int = 200) -> List[Dict[str, Any]]:
        """Retrieve stored conversation history with peer."""
        current_user = self.client.current_user or ""
        return self.db.get_conversation_history(current_user, peer, limit)
