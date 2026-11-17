# Application Architecture Specification
## Encrypted LAN Chat & File Sharing System
**Author:** Tanay Sharma (23ESKCY051, CSL-G56)

---

## 1. Architectural Philosophy
The application follows a decoupled, service-oriented desktop architecture designed around five principles:
1. **Zero-Trust Network Model:** The server is strictly a routing hub. All end-to-end payload encryption occurs at the client endpoints.
2. **Deterministic Packet Framing:** Sockets use 4-byte big-endian length prefixing to prevent TCP packet coalescence and fragmentation bugs.
3. **Thread Safety & Non-Blocking GUI:** All socket I/O, cryptographic derivation, and disk transfers operate in background threads and dispatch UI changes to the main thread via event queues.
4. **Data Isolation:** Local data is managed by thread-local SQLite connections with Write-Ahead Logging (`WAL`).
5. **Defense in Depth:** Defense mechanisms exist at every layer: input sanitization, rate limiting, AEAD tags, and post-assembly SHA-256 checks.

---

## 2. Directory and Component Breakdown

```
encrypted-lan-chat/
├── main.py                  # CLI entry point, screen switcher, Tkinter lifecycle
├── config.py                # System-wide configuration, cryptographic parameters, theme
├── requirements.txt         # Runtime and development dependencies
├── README.md                # Installation and multi-node execution guide
│
├── app/
│   ├── authentication.py    # Argon2id hashing, credential validation, sessions
│   ├── database.py          # SQLite WAL connection manager, parameterized queries
│   ├── server.py            # Multithreaded TCP server with presence and blind routing
│   ├── client.py            # Client TCP socket manager, framing, background receiver
│   ├── network_manager.py   # High-level orchestrator binding network, auth, and GUI
│   ├── encryption.py        # AES-256-GCM AEAD, random nonces, SHA-256 hashing
│   ├── key_exchange.py      # X25519 Curve25519 Diffie-Hellman & HKDF key derivation
│   ├── messaging.py         # End-to-end encrypted messaging service & local history
│   ├── file_transfer.py     # 64 KB chunked transfer, progress tracking, path sanitization
│   └── protocol.py          # Packet framing, JSON schema packing, unpack validation
│
├── gui/
│   ├── login.py             # Login card, server IP/port entry, host server launcher
│   ├── register.py          # Registration interface with password strength validation
│   ├── dashboard.py         # 3-pane layout: navigation sidebar, center view, user list
│   ├── chat.py              # Message bubbles, header encryption badges, text entry
│   ├── file_sharing.py      # File picker, hash preview, progress bars, receive modal
│   ├── server_manager.py    # GUI server control, local LAN IP display, client table, logs
│   ├── settings.py          # Downloads directory selector, password change, crypto specs
│   ├── history.py           # Past transfers table, directions, hashes, status
│   └── components.py        # Reusable badges, styled cards, message bubble frames
│
├── database/
│   └── schema.sql           # SQLite table schemas and performance indices
│
├── storage/
│   └── downloads/           # Dedicated directory for decrypted, verified files
│
├── tests/
│   ├── test_auth.py         # Authentication, rate limiting, and password hashing tests
│   ├── test_encryption.py   # AES-GCM, nonce uniqueness, tampering rejection tests
│   ├── test_key_exchange.py # X25519 DH handshake and HKDF symmetry tests
│   ├── test_protocol.py     # Length prefixing, frame packing, corrupt JSON tests
│   ├── test_network.py      # Concurrent client connections, presence broadcast tests
│   ├── test_messaging.py    # E2E encrypted message flow through server
│   └── test_file_transfer.py# Chunked transfer, SHA-256 validation, path traversal tests
│
└── docs/
    ├── PROJECT_REPORT.md    # Comprehensive academic syllabus report
    ├── ARCHITECTURE.md      # This architectural specification
    └── SECURITY.md          # Threat model, cryptographic parameters, attack mitigations
```

---

## 3. Communication Protocol Specification

### Packet Framing Header
All socket transmissions prepend a 4-byte big-endian unsigned integer representing payload length:

```
+-----------------------------------+-----------------------------------------+
|   Length Prefix (4 Bytes, !I)     |         JSON UTF-8 Payload Bytes        |
|    e.g. 0x00 0x00 0x01 0x2A       |    {"type": "CHAT_MESSAGE", ...}        |
+-----------------------------------+-----------------------------------------+
```

### JSON Schema
```json
{
  "type": "STRING (e.g. CHAT_MESSAGE, FILE_CHUNK, KEY_EXCHANGE_INIT)",
  "msg_id": "UUID v4 string",
  "sender": "sender_username",
  "receiver": "recipient_username | SERVER | BROADCAST",
  "timestamp": "ISO-8601 UTC timestamp",
  "payload": { ... }
}
```

---

## 4. Concurrency & Threading Model

To ensure the CustomTkinter GUI remains smooth (60 FPS) without freezing during network transfers:
1. **Client Receiver Thread (`_listen_loop`):** Continuously blocks on `recv_exact` in the background, parses completed frames, and routes packets.
2. **Heartbeat Thread (`_heartbeat_loop`):** Emits `HEARTBEAT_PING` every 15 seconds to monitor connection health.
3. **File Transfer Worker Threads (`_stream_file_chunks`):** Separate thread per file upload so large transfers do not block chat messaging.
4. **Server Handler Threads (`_handle_client_connection`):** One dedicated thread per connected client socket.
5. **Main Thread Dispatching:** Network callbacks invoke `widget.after(0, callback)` so all UI mutations occur safely on Tkinter's main thread.
