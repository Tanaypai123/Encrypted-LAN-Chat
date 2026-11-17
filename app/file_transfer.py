"""
Encrypted File Transfer Subsystem.
Implements chunked file transfer, per-chunk AES-256-GCM encryption with unique nonces,
SHA-256 integrity validation, path traversal prevention, and background thread execution.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import os
import base64
import math
import uuid
import time
import threading
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List

from config import (
    FILE_CHUNK_SIZE,
    DOWNLOADS_DIR,
    MAX_FILE_SIZE_BYTES
)
from app.protocol import ProtocolMessageType, create_message
from app.encryption import (
    encrypt_bytes,
    decrypt_bytes,
    compute_file_sha256,
    compute_bytes_sha256,
    TamperedMessageError,
    DecryptionError
)
from app.key_exchange import KeyExchangeManager
from app.database import DatabaseManager

logger = logging.getLogger("FileTransferService")

def sanitize_filename(filename: str) -> str:
    """
    Sanitize received filename to prevent path traversal attacks.
    Strips directory separators (both Windows backslash and Unix slash),
    null bytes, and parent path tokens.
    """
    normalized = filename.replace("\\", "/").strip()
    cleaned = os.path.basename(normalized).strip()
    cleaned = "".join(c for c in cleaned if c.isprintable() and c not in '\\/:*?"<>|')
    cleaned = cleaned.lstrip(".")
    if not cleaned:
        cleaned = f"file_{int(time.time())}.dat"
    return cleaned

class FileTransferTask:
    """Represents an ongoing inbound or outbound file transfer."""

    def __init__(
        self,
        transfer_id: str,
        filename: str,
        file_size: int,
        sha256_hash: str,
        sender: str,
        receiver: str,
        is_outgoing: bool,
        local_path: Optional[str] = None
    ):
        self.transfer_id = transfer_id
        self.filename = filename
        self.file_size = file_size
        self.sha256_hash = sha256_hash
        self.sender = sender
        self.receiver = receiver
        self.is_outgoing = is_outgoing
        self.local_path = local_path

        self.bytes_transferred = 0
        self.total_chunks = math.ceil(file_size / FILE_CHUNK_SIZE) if file_size > 0 else 1
        self.chunks_completed = 0
        self.status = "pending"  # pending, transferring, completed, failed, rejected, cancelled
        self.progress_percent = 0.0
        self.start_time = time.time()
        self.temp_file_path: Optional[Path] = None

class FileTransferService:
    """Manages secure chunked file transfers over LAN."""

    def __init__(
        self,
        client: Any,
        key_mgr: KeyExchangeManager,
        db_mgr: Optional[DatabaseManager] = None,
        downloads_dir: Optional[Path] = None,
        on_transfer_request: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_progress_update: Optional[Callable[[str, float, str, int, int], None]] = None,
        on_transfer_complete: Optional[Callable[[str, str, bool, str], None]] = None,
        on_system_alert: Optional[Callable[[str, str], None]] = None
    ):
        self.client = client
        self.key_mgr = key_mgr
        self.db = db_mgr or DatabaseManager.get_instance()
        self.downloads_dir = Path(downloads_dir or DOWNLOADS_DIR)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

        self.on_transfer_request = on_transfer_request or (lambda req: None)
        self.on_progress_update = on_progress_update or (lambda tid, pct, status, b_done, b_total: None)
        self.on_transfer_complete = on_transfer_complete or (lambda tid, path, success, msg: None)
        self.on_system_alert = on_system_alert or (lambda lvl, msg: None)

        self._transfers: Dict[str, FileTransferTask] = {}
        self._lock = threading.Lock()
        self._active_workers: Dict[str, threading.Thread] = {}

    def send_file(self, receiver: str, file_path: str) -> Optional[str]:
        """Initiate encrypted file transfer to peer."""
        path = Path(file_path).resolve()
        if not path.exists() or not path.is_file():
            self.on_system_alert("error", f"File does not exist: {file_path}")
            return None

        file_size = path.stat().st_size
        if file_size > MAX_FILE_SIZE_BYTES:
            self.on_system_alert("error", f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB.")
            return None

        # Ensure E2E session key exists with receiver
        if not self.key_mgr.has_session_key(receiver):
            self.on_system_alert("warning", f"Establishing secure key exchange with {receiver} first...")
            pub_b64 = self.key_mgr.initiate_handshake(receiver)
            self.client.send_message(
                ProtocolMessageType.KEY_EXCHANGE_INIT,
                receiver=receiver,
                payload={"public_key": pub_b64}
            )

        # Compute SHA-256 checksum before sending
        sha256 = compute_file_sha256(str(path))
        transfer_id = str(uuid.uuid4())
        filename = path.name
        sender = self.client.current_user or "unknown"

        task = FileTransferTask(
            transfer_id=transfer_id,
            filename=filename,
            file_size=file_size,
            sha256_hash=sha256,
            sender=sender,
            receiver=receiver,
            is_outgoing=True,
            local_path=str(path)
        )

        with self._lock:
            self._transfers[transfer_id] = task

        # Record in database
        self.db.record_file_transfer(
            transfer_id=transfer_id,
            filename=filename,
            file_size=file_size,
            sender=sender,
            receiver=receiver,
            sha256_hash=sha256,
            local_path=str(path),
            status="pending"
        )

        # Send file transfer request to peer
        self.client.send_message(
            ProtocolMessageType.FILE_TRANSFER_REQUEST,
            receiver=receiver,
            payload={
                "transfer_id": transfer_id,
                "filename": filename,
                "file_size": file_size,
                "sha256_hash": sha256
            }
        )
        self.on_progress_update(transfer_id, 0.0, "Waiting for recipient to accept...", 0, file_size)
        return transfer_id

    def accept_transfer(self, transfer_id: str, custom_download_path: Optional[str] = None) -> bool:
        """Accept an incoming file transfer request."""
        with self._lock:
            task = self._transfers.get(transfer_id)
            if not task:
                return False

            save_dir = Path(custom_download_path) if custom_download_path else self.downloads_dir
            save_dir.mkdir(parents=True, exist_ok=True)

            safe_name = sanitize_filename(task.filename)
            target_path = save_dir / safe_name

            # Avoid overwriting existing files
            counter = 1
            stem = target_path.stem
            suffix = target_path.suffix
            while target_path.exists():
                target_path = save_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            task.local_path = str(target_path)
            task.temp_file_path = save_dir / f".{safe_name}.{transfer_id}.part"
            task.status = "transferring"

        # Initialize empty temp file
        with open(task.temp_file_path, "wb") as f:
            pass

        # Send acceptance
        self.client.send_message(
            ProtocolMessageType.FILE_TRANSFER_ACCEPT,
            receiver=task.sender,
            payload={"transfer_id": transfer_id}
        )
        self.db.update_file_transfer_progress(transfer_id, 0.0, "transferring")
        self.on_progress_update(transfer_id, 0.0, "Transfer in progress...", 0, task.file_size)
        return True

    def reject_transfer(self, transfer_id: str):
        """Reject an incoming file transfer request."""
        with self._lock:
            task = self._transfers.get(transfer_id)
            if not task:
                return
            task.status = "rejected"

        self.client.send_message(
            ProtocolMessageType.FILE_TRANSFER_REJECT,
            receiver=task.sender,
            payload={"transfer_id": transfer_id}
        )
        self.db.complete_file_transfer(transfer_id, status="rejected")
        self.on_progress_update(transfer_id, 0.0, "Transfer rejected", 0, task.file_size)

    def handle_protocol_message(self, msg: Dict[str, Any]) -> bool:
        """Route protocol packets for file transfer."""
        msg_type = msg.get("type")
        sender = msg.get("sender")
        payload = msg.get("payload", {})
        transfer_id = payload.get("transfer_id")

        if msg_type == ProtocolMessageType.FILE_TRANSFER_REQUEST:
            self._handle_incoming_request(sender, payload)
            return True

        elif msg_type == ProtocolMessageType.FILE_TRANSFER_ACCEPT:
            self._handle_transfer_accepted(transfer_id)
            return True

        elif msg_type == ProtocolMessageType.FILE_TRANSFER_REJECT:
            self._handle_transfer_rejected(transfer_id)
            return True

        elif msg_type == ProtocolMessageType.FILE_CHUNK:
            self._handle_incoming_chunk(sender, payload)
            return True

        elif msg_type == ProtocolMessageType.FILE_TRANSFER_COMPLETE:
            self._handle_transfer_complete(sender, payload)
            return True

        return False

    def _handle_incoming_request(self, sender: str, payload: Dict[str, Any]):
        """Process incoming file transfer offering."""
        transfer_id = payload["transfer_id"]
        filename = sanitize_filename(payload["filename"])
        file_size = payload["file_size"]
        sha256_hash = payload["sha256_hash"]
        current_user = self.client.current_user or ""

        task = FileTransferTask(
            transfer_id=transfer_id,
            filename=filename,
            file_size=file_size,
            sha256_hash=sha256_hash,
            sender=sender,
            receiver=current_user,
            is_outgoing=False
        )

        with self._lock:
            self._transfers[transfer_id] = task

        self.db.record_file_transfer(
            transfer_id=transfer_id,
            filename=filename,
            file_size=file_size,
            sender=sender,
            receiver=current_user,
            sha256_hash=sha256_hash,
            status="pending"
        )

        # Notify UI to prompt user or show incoming transfer
        self.on_transfer_request({
            "transfer_id": transfer_id,
            "filename": filename,
            "file_size": file_size,
            "sender": sender,
            "sha256": sha256_hash
        })

    def _handle_transfer_accepted(self, transfer_id: str):
        """Peer accepted our file offer. Start chunked background streaming."""
        with self._lock:
            task = self._transfers.get(transfer_id)
            if not task:
                return
            task.status = "transferring"

        self.db.update_file_transfer_progress(transfer_id, 0.0, "transferring")

        # Launch worker thread
        t = threading.Thread(target=self._stream_file_chunks, args=(task,), daemon=True)
        with self._lock:
            self._active_workers[transfer_id] = t
        t.start()

    def _handle_transfer_rejected(self, transfer_id: str):
        """Peer rejected file transfer."""
        with self._lock:
            task = self._transfers.get(transfer_id)
            if task:
                task.status = "rejected"
        self.db.complete_file_transfer(transfer_id, status="rejected")
        self.on_transfer_complete(transfer_id, "", False, "Transfer rejected by recipient.")

    def _stream_file_chunks(self, task: FileTransferTask):
        """Worker thread to read, encrypt, and stream chunks to receiver."""
        session_key = self.key_mgr.get_session_key(task.receiver)
        if not session_key:
            self.on_system_alert("error", f"No encryption key for '{task.receiver}'. Aborting transfer.")
            self._mark_transfer_failed(task, "Session key missing")
            return

        try:
            chunk_index = 0
            with open(task.local_path, "rb") as f:
                while True:
                    chunk_bytes = f.read(FILE_CHUNK_SIZE)
                    if not chunk_bytes:
                        break

                    # Encrypt chunk with AES-256-GCM using unique nonce
                    ciphertext, nonce = encrypt_bytes(chunk_bytes, session_key)

                    payload = {
                        "transfer_id": task.transfer_id,
                        "chunk_index": chunk_index,
                        "total_chunks": task.total_chunks,
                        "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
                        "nonce": base64.b64encode(nonce).decode("utf-8"),
                        "chunk_hash": compute_bytes_sha256(chunk_bytes)
                    }

                    success = self.client.send_message(
                        ProtocolMessageType.FILE_CHUNK,
                        receiver=task.receiver,
                        payload=payload
                    )
                    if not success:
                        self._mark_transfer_failed(task, "Connection lost during transfer")
                        return

                    task.bytes_transferred += len(chunk_bytes)
                    task.chunks_completed += 1
                    pct = (task.bytes_transferred / task.file_size) * 100.0 if task.file_size > 0 else 100.0
                    task.progress_percent = pct

                    # Update database and UI
                    self.db.update_file_transfer_progress(task.transfer_id, pct)
                    self.on_progress_update(
                        task.transfer_id,
                        pct,
                        "Sending...",
                        task.bytes_transferred,
                        task.file_size
                    )

                    chunk_index += 1
                    # Brief sleep to avoid overwhelming socket buffer on massive transfers
                    time.sleep(0.001)

            # Signal sender finish
            self.client.send_message(
                ProtocolMessageType.FILE_TRANSFER_COMPLETE,
                receiver=task.receiver,
                payload={"transfer_id": task.transfer_id, "sha256_hash": task.sha256_hash}
            )

            task.status = "completed"
            self.db.complete_file_transfer(task.transfer_id, "completed", task.local_path)
            self.on_transfer_complete(task.transfer_id, task.local_path or "", True, "File sent successfully!")

        except Exception as e:
            logger.error(f"Error streaming file chunks for {task.transfer_id}: {e}")
            self._mark_transfer_failed(task, str(e))

    def _handle_incoming_chunk(self, sender: str, payload: Dict[str, Any]):
        """Receive, decrypt, and append file chunk."""
        transfer_id = payload["transfer_id"]
        with self._lock:
            task = self._transfers.get(transfer_id)
            if not task or not task.temp_file_path:
                return

        session_key = self.key_mgr.get_session_key(sender)
        if not session_key:
            self._mark_transfer_failed(task, "Session key missing for decryption")
            return

        try:
            ciphertext = base64.b64decode(payload["ciphertext"])
            nonce = base64.b64decode(payload["nonce"])
            expected_chunk_hash = payload.get("chunk_hash")

            decrypted_chunk = decrypt_bytes(ciphertext, nonce, session_key)

            if expected_chunk_hash:
                actual_chunk_hash = compute_bytes_sha256(decrypted_chunk)
                if actual_chunk_hash != expected_chunk_hash:
                    raise TamperedMessageError(f"Chunk hash mismatch! Expected {expected_chunk_hash}, got {actual_chunk_hash}")

            # Append to temporary assembly file
            with open(task.temp_file_path, "ab") as f:
                f.write(decrypted_chunk)

            task.bytes_transferred += len(decrypted_chunk)
            task.chunks_completed += 1
            pct = (task.bytes_transferred / task.file_size) * 100.0 if task.file_size > 0 else 100.0
            task.progress_percent = pct

            self.db.update_file_transfer_progress(task.transfer_id, pct)
            self.on_progress_update(
                task.transfer_id,
                pct,
                "Receiving...",
                task.bytes_transferred,
                task.file_size
            )

        except (TamperedMessageError, DecryptionError) as e:
            logger.critical(f"Integrity failure in file transfer {transfer_id}: {e}")
            self._mark_transfer_failed(task, f"Integrity check failed: {e}")
            self.on_system_alert("critical", f"SECURITY ALERT: Received tampered file chunk for '{task.filename}'!")
        except Exception as e:
            logger.error(f"Failed to process chunk for {transfer_id}: {e}")
            self._mark_transfer_failed(task, str(e))

    def _handle_transfer_complete(self, sender: str, payload: Dict[str, Any]):
        """Sender finished. Validate final SHA-256 integrity and move temp file."""
        transfer_id = payload["transfer_id"]
        with self._lock:
            task = self._transfers.get(transfer_id)
            if not task:
                return

        if not task.temp_file_path or not task.temp_file_path.exists():
            self._mark_transfer_failed(task, "Incomplete or missing temporary transfer file.")
            return

        try:
            # Verify full file SHA-256
            assembled_hash = compute_file_sha256(str(task.temp_file_path))
            if assembled_hash.lower() != task.sha256_hash.lower():
                # Hash mismatch! Possible corruption or tampering
                if task.temp_file_path.exists():
                    task.temp_file_path.unlink()
                err_msg = f"SHA-256 mismatch! Expected {task.sha256_hash}, calculated {assembled_hash}"
                self._mark_transfer_failed(task, err_msg)
                self.on_system_alert("critical", f"FILE INTEGRITY ERROR: Checksum failed for '{task.filename}'! File discarded.")
                return

            # Checksum matches! Rename temp file to final path
            final_path = Path(task.local_path)
            task.temp_file_path.rename(final_path)

            task.status = "completed"
            task.progress_percent = 100.0
            self.db.complete_file_transfer(task.transfer_id, "completed", str(final_path))
            self.on_progress_update(task.transfer_id, 100.0, "Verified & Saved", task.file_size, task.file_size)
            self.on_transfer_complete(task.transfer_id, str(final_path), True, f"File verified (SHA-256 OK) and saved to {final_path.name}")

        except Exception as e:
            logger.error(f"Error finalizing file transfer {transfer_id}: {e}")
            self._mark_transfer_failed(task, str(e))

    def _mark_transfer_failed(self, task: FileTransferTask, reason: str):
        """Mark task as failed and clean up temp files."""
        task.status = "failed"
        if task.temp_file_path and task.temp_file_path.exists():
            try:
                task.temp_file_path.unlink()
            except Exception:
                pass
        self.db.complete_file_transfer(task.transfer_id, "failed")
        self.on_transfer_complete(task.transfer_id, "", False, f"Transfer failed: {reason}")
        self.on_progress_update(task.transfer_id, task.progress_percent, f"Failed: {reason}", task.bytes_transferred, task.file_size)

    def get_transfer_history(self) -> List[Dict[str, Any]]:
        """Fetch all transfer records from database."""
        current_user = self.client.current_user
        return self.db.get_transfer_history(current_user)
