"""
Network Communication Protocol and Length-Prefixed Packet Framing.
Provides structured JSON message schemas and deterministic network serialization.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import json
import struct
import socket
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from config import HEADER_LENGTH_BYTES

MAX_FRAME_SIZE = 32 * 1024 * 1024  # 32 MB maximum frame size to prevent DoS memory exhaustion

class ProtocolMessageType:
    # Authentication & Session
    AUTH_REQUEST = "AUTH_REQUEST"
    AUTH_RESPONSE = "AUTH_RESPONSE"
    LOGOUT_NOTIFY = "LOGOUT_NOTIFY"

    # Presence & Discovery
    USER_LIST_REQUEST = "USER_LIST_REQUEST"
    USER_LIST_UPDATE = "USER_LIST_UPDATE"
    USER_STATUS_CHANGE = "USER_STATUS_CHANGE"
    HEARTBEAT_PING = "HEARTBEAT_PING"
    HEARTBEAT_PONG = "HEARTBEAT_PONG"

    # Key Exchange (End-to-End Cryptography)
    KEY_EXCHANGE_INIT = "KEY_EXCHANGE_INIT"
    KEY_EXCHANGE_REPLY = "KEY_EXCHANGE_REPLY"

    # Messaging
    CHAT_MESSAGE = "CHAT_MESSAGE"
    MESSAGE_ACK = "MESSAGE_ACK"

    # File Transfer
    FILE_TRANSFER_REQUEST = "FILE_TRANSFER_REQUEST"
    FILE_TRANSFER_ACCEPT = "FILE_TRANSFER_ACCEPT"
    FILE_TRANSFER_REJECT = "FILE_TRANSFER_REJECT"
    FILE_CHUNK = "FILE_CHUNK"
    FILE_TRANSFER_COMPLETE = "FILE_TRANSFER_COMPLETE"
    FILE_TRANSFER_CANCEL = "FILE_TRANSFER_CANCEL"

    # Error Reporting
    ERROR = "ERROR"

class ProtocolError(Exception):
    """Exception raised for invalid packet framing or corrupted protocol data."""
    pass

def create_message(
    msg_type: str,
    sender: str,
    receiver: str,
    payload: Optional[Dict[str, Any]] = None,
    msg_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a standardized protocol message dictionary."""
    return {
        "type": msg_type,
        "msg_id": msg_id or str(uuid.uuid4()),
        "sender": sender,
        "receiver": receiver,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload or {}
    }

def pack_message(message_dict: Dict[str, Any]) -> bytes:
    """
    Serialize message dict to UTF-8 JSON and prepend a 4-byte big-endian length prefix.
    """
    json_bytes = json.dumps(message_dict, ensure_ascii=False).encode("utf-8")
    length = len(json_bytes)
    if length > MAX_FRAME_SIZE:
        raise ProtocolError(f"Message size {length} exceeds maximum frame limit of {MAX_FRAME_SIZE} bytes.")
    header = struct.pack("!I", length)
    return header + json_bytes

def unpack_message(raw_bytes: bytes) -> Dict[str, Any]:
    """Parse JSON payload bytes into a dictionary."""
    try:
        data = json.loads(raw_bytes.decode("utf-8"))
        if not isinstance(data, dict):
            raise ProtocolError("Decoded packet is not a valid JSON object.")
        required_fields = {"type", "msg_id", "sender", "receiver", "timestamp", "payload"}
        if not required_fields.issubset(data.keys()):
            raise ProtocolError(f"Missing required protocol fields: {required_fields - set(data.keys())}")
        return data
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ProtocolError(f"Failed to decode message JSON: {e}")

def send_framed_message(sock: socket.socket, message_dict: Dict[str, Any]):
    """Send length-prefixed packet over socket."""
    packet = pack_message(message_dict)
    sock.sendall(packet)

def recv_exact(sock: socket.socket, num_bytes: int) -> bytes:
    """Read exactly num_bytes from socket, handling TCP fragmentation."""
    buffer = bytearray()
    while len(buffer) < num_bytes:
        chunk = sock.recv(min(num_bytes - len(buffer), 65536))
        if not chunk:
            raise ConnectionResetError("Connection closed while receiving packet.")
        buffer.extend(chunk)
    return bytes(buffer)

def recv_framed_message(sock: socket.socket) -> Dict[str, Any]:
    """
    Read length-prefixed frame from socket and parse into a dictionary.
    Raises ConnectionResetError if connection drops.
    """
    # Read 4-byte header
    header_bytes = recv_exact(sock, HEADER_LENGTH_BYTES)
    (length,) = struct.unpack("!I", header_bytes)

    if length > MAX_FRAME_SIZE:
        raise ProtocolError(f"Frame length {length} exceeds maximum allowed size ({MAX_FRAME_SIZE} bytes).")

    # Read exactly 'length' payload bytes
    payload_bytes = recv_exact(sock, length)
    return unpack_message(payload_bytes)
