# COLLEGE PROJECT REPORT
## Encrypted LAN Chat & File Sharing System (GUI)

---

### **Project Metadata**
- **Student Name:** Tanay Sharma
- **University ID:** 23ESKCY051
- **Subject Code:** 23ESKCY051
- **Project Group:** CSL-G56
- **Project Type:** Syllabus Project
- **Application Type:** GUI-based Desktop Application
- **Primary Language:** Python 3.11+
- **Date:** November 2026

---

## 1. Project Introduction
In modern enterprise and academic settings, collaborative teams frequently communicate and exchange sensitive digital assets over local networks (LANs). However, conventional LAN communication tools either broadcast plaintext packets over insecure subnets or depend on third-party cloud infrastructure that subjects confidential organizational data to external surveillance, data breaches, and internet bandwidth consumption.

The **Encrypted LAN Chat & File Sharing System** is a standalone, high-performance, and secure desktop application engineered to provide confidential real-time text communication and chunked file transfers across computers connected to the same Local Area Network (Wi-Fi or Ethernet). Designed with a zero-trust cryptographic posture, the system ensures that message payloads and file contents are never transmitted in plaintext and cannot be decrypted by network eavesdroppers or rogue routers.

---

## 2. Problem Statement
Traditional communication frameworks operate under two disadvantageous paradigms:
1. **Cloud-Dependent Services (e.g., Slack, WhatsApp, Google Drive):** Require constant external internet connectivity, route local intranet traffic through remote servers, and introduce latency, regulatory compliance concerns, and telemetry exposure.
2. **Insecure Local Network Tools (e.g., plain socket tools, legacy netcat, FTP):** Transmit cleartext TCP/UDP packets across the LAN. On shared Wi-Fi networks or unsegmented corporate switches, adversaries employing Address Resolution Protocol (ARP) spoofing or packet sniffing tools (e.g., Wireshark) can reconstruct messages and exfiltrate files effortlessly.

There is a pronounced need for a self-hosted, decentralized, and cryptographically verified application capable of operating entirely on local networks without requiring internet access, cloud servers, or subscription dependencies.

---

## 3. Objectives
The core objectives of the system are:
1. **Confidentiality:** Implement authenticated symmetric encryption (AES-256-GCM) for both real-time text messages and chunked file transfers.
2. **End-to-End Key Agreement:** Facilitate peer-to-peer ephemeral key derivation using Curve25519 (X25519) and HKDF-SHA256, guaranteeing that the relay server cannot inspect message payloads.
3. **Data Integrity:** Prevent packet tampering, bit-flipping, and replay attacks by validating cryptographic message authentication codes (MACs) and SHA-256 file hashes.
4. **Secure Authentication & Identity Management:** Provide local account registration and login protected by Argon2id password hashing and brute-force rate limiting.
5. **Robust Chunked File Sharing:** Enable resilient transmission of files of arbitrary sizes via 64 KB encrypted chunks without memory exhaustion, incorporating path traversal sanitization.
6. **Modern Desktop User Interface:** Deliver an ergonomic GUI built with CustomTkinter following contemporary dark-theme human interface guidelines.

---

## 4. Scope
The scope of this project encompasses:
- Deployment on workstations within any IPv4 local area subnet (Wi-Fi or Ethernet).
- Cross-platform support across macOS, Microsoft Windows, and Linux distributions.
- Multi-client concurrent connectivity to a user-hosted local server.
- Private 1-to-1 encrypted conversations and dynamic user presence tracking.
- Secure file exchange with real-time transfer progress and checksum verification.
- Offline and air-gapped network usability.

---

## 5. Existing System vs. Proposed System

| Feature / Metric | Conventional LAN Systems (FTP, IRC, Plain Sockets) | Cloud Tools (Slack, Teams, WhatsApp) | Proposed System (Encrypted LAN Chat) |
| :--- | :--- | :--- | :--- |
| **Internet Dependency** | None | Mandatory | **None (100% Local LAN)** |
| **Transport Security** | None (Plaintext / Cleartext) | TLS to Cloud Servers | **AES-256-GCM + X25519 E2E** |
| **Server Trust Model** | Server inspects all packets | Cloud provider inspects metadata/data | **Zero-Trust (Server is Blind Relay)** |
| **File Integrity** | Optional / Rare (Plain CRC32) | Cloud-managed | **Per-chunk MAC + Full SHA-256 Checksum** |
| **Password Storage** | Plaintext or basic MD5/SHA-1 | Cloud Identity Provider | **Argon2id Memory-Hard Hashing** |
| **Interface** | Outdated CLI or legacy Tkinter | Proprietary Web/Electron | **Modern Dark CustomTkinter GUI** |
| **Path Traversal Defense** | Absent | Server-side | **Strict Basename & Null-Byte Sanitizer** |

---

## 6. Hardware & Software Requirements

### Hardware Requirements
- **Processor:** Dual-Core 1.8 GHz 64-bit CPU or higher (x86_64 or Apple Silicon ARM64).
- **RAM:** 2 GB minimum (4 GB recommended).
- **Storage:** 100 MB free disk space for runtime and application logs (plus user storage for downloaded files).
- **Network Interface Card (NIC):** Standard 802.11 b/g/n/ac Wi-Fi adapter or 10/100/1000 Mbps Ethernet port.

### Software Requirements
- **Operating System:** macOS 11+, Windows 10/11, or Linux (Ubuntu 20.04+, Debian, Fedora).
- **Runtime Environment:** Python 3.11 or Python 3.12.
- **Primary Dependencies:**
  - `customtkinter>=5.2.0` (GUI Framework)
  - `cryptography>=41.0.0` (AES-256-GCM, X25519, HKDF)
  - `argon2-cffi>=23.1.0` (Argon2id password hashing)
  - `pillow>=10.0.0` (Image processing)
  - `pytest>=7.4.0` (Automated verification)

---

## 7. System Architecture

The application adopts a modular, layered service-oriented architecture:

```
+-------------------------------------------------------------------------+
|                         CustomTkinter GUI Layer                         |
|   (Login, Registration, Dashboard, Chat, File Sharing, Server Manager)  |
+------------------------------------+------------------------------------+
                                     |
+------------------------------------+------------------------------------+
|                         Network Manager                                 |
|            (Unified Controller, Event Dispatcher, State Store)          |
+-------------------+----------------+-------------------+----------------+
                    |                |                   |
+-------------------+---+  +---------+---------+  +------+----------------+
|   Messaging Service   |  | File Transfer Svc |  |  Authentication Mgr  |
| (E2E Chat Orchestrator|  | (Chunking, SHA256,|  | (Argon2id, Validation,|
|  & History Persistence|  |  Progress, Traver)|  |  Session Management) |
+-------------------+---+  +---------+---------+  +------+----------------+
                    |                |                   |
+-------------------+----------------+-------------------+----------------+
|                         Cryptographic Engine                            |
|        (AES-256-GCM AEAD, X25519 ECDH, HKDF-SHA256, Secure Nonces)      |
+------------------------------------+------------------------------------+
                                     |
+------------------------------------+------------------------------------+
|                       TCP Transport & Protocol                          |
|         (Length-Prefixed Framing, Sockets, Multi-threading)             |
+------------------------------------+------------------------------------+
                                     |
+------------------------------------+------------------------------------+
|                     SQLite Local Database Layer                         |
|     (WAL Mode, Parameterized Queries, Audit Trails, History Archives)   |
+-------------------------------------------------------------------------+
```

---

## 8. Data Flow Diagrams (DFD)

### Level 0 DFD (Context Diagram)
```
  +--------------+                                      +---------------+
  |              |        Register / Login Request      |               |
  |              | -----------------------------------> |               |
  |              | <----------------------------------- |               |
  | Client User  |         Auth Token & Peer List       |  LAN Server   |
  |   (Alice)    |                                      |   (Router &   |
  |              |        Encrypted Packets (Relayed)   |   Directory)  |
  |              | ===================================> |               |
  +--------------+                                      +-------+-------+
                                                                |
                                  Relayed Encrypted Packets     |
                                  (Server cannot inspect)       |
                                                                v
                                                        +---------------+
                                                        |  Client User  |
                                                        |     (Bob)     |
                                                        +---------------+
```

### Level 1 DFD (End-to-End Encrypted Message Flow)
1. **Key Agreement:**
   - Alice creates an ephemeral Curve25519 key pair $(sk_A, pk_A)$ and transmits $pk_A$ via server to Bob.
   - Bob receives $pk_A$, creates $(sk_B, pk_B)$, derives $K = \text{HKDF}(sk_B \cdot pk_A)$, and transmits $pk_B$ back to Alice.
   - Alice derives $K = \text{HKDF}(sk_A \cdot pk_B)$. Both hold identical 256-bit symmetric key $K$.
2. **Message Transmission:**
   - Alice generates a 12-byte random nonce $N$.
   - Payload is encrypted: $(C, T) = \text{AES-GCM-Encrypt}(K, N, \text{Plaintext})$.
   - JSON packet with $(C, T, N)$ is serialized with a 4-byte length header and transmitted over TCP.
3. **Receipt and Validation:**
   - Bob's socket listener frames the packet.
   - Bob verifies $T$ and decrypts $C$ using $K$ and $N$.
   - If verified, message is displayed in GUI and stored in local SQLite.

---

## 9. Database Design

The local SQLite schema operates in Write-Ahead Logging (`WAL`) mode with parameterized queries:

1. **`users` Table:**
   - `id` (INTEGER PRIMARY KEY)
   - `username` (TEXT UNIQUE)
   - `password_hash` (TEXT)
   - `salt` (TEXT)
   - `algorithm` (TEXT DEFAULT 'argon2id')
   - `created_at` (TIMESTAMP)
   - `last_login` (TIMESTAMP)
   - `is_active` (INTEGER)

2. **`messages` Table:**
   - `id` (INTEGER PRIMARY KEY)
   - `msg_id` (TEXT UNIQUE)
   - `sender_username` (TEXT)
   - `receiver_username` (TEXT)
   - `message_content` (TEXT)
   - `is_encrypted` (INTEGER)
   - `timestamp` (TIMESTAMP)
   - `delivery_status` (TEXT)

3. **`file_transfers` Table:**
   - `id` (INTEGER PRIMARY KEY)
   - `transfer_id` (TEXT UNIQUE)
   - `filename` (TEXT)
   - `file_size` (INTEGER)
   - `sender_username` (TEXT)
   - `receiver_username` (TEXT)
   - `sha256_hash` (TEXT)
   - `status` (TEXT)
   - `progress` (REAL)
   - `local_path` (TEXT)
   - `created_at` (TIMESTAMP)
   - `completed_at` (TIMESTAMP)

4. **`auth_attempts` Table (Rate Limiting):**
   - `id` (INTEGER PRIMARY KEY)
   - `identifier` (TEXT)
   - `attempt_time` (TIMESTAMP)
   - `success` (INTEGER)

---

## 10. Encryption Methodology

### Authenticated Encryption (AES-256-GCM)
Galois/Counter Mode (GCM) combines counter-mode confidentiality with polynomial Galois MAC authentication. For every message and file chunk:
$$\text{Ciphertext}, \text{Tag} = \text{AES-256-GCM-Encrypt}(K_{\text{session}}, \text{Nonce}, \text{Plaintext})$$
- Key Length: 256 bits (32 bytes).
- Nonce Length: 96 bits (12 bytes) drawn from cryptographically secure entropy (`os.urandom`).
- Tag Length: 128 bits (16 bytes).

### Ephemeral Elliptic Curve Diffie-Hellman (X25519)
Curve25519 offers 128-bit security level, immune to timing side-channel vulnerabilities:
$$\text{Shared Secret} = X25519(sk_{\text{local}}, pk_{\text{peer}})$$
The raw scalar multiplication result is expanded into a symmetric key via HKDF:
$$K_{\text{session}} = \text{HKDF-Extract-and-Expand}(\text{Secret}, \text{salt}=\text{None}, \text{info}=\text{"lan-chat-v1-session-key"}, \text{len}=32)$$

### Password Security (Argon2id)
Argon2id (winner of the Password Hashing Competition) combines data-independent and data-dependent memory access to counter both side-channel attacks and GPU/ASIC brute forcing:
- Memory Cost: 64 MB ($65,536\text{ KB}$)
- Time Cost: 3 iterations
- Parallelism: 4 lanes
- Unique 16-byte random salt per user.

---

## 11. Implementation Details
The application codebase is strictly decoupled into modular subsystems:
- **`config.py`:** Network defaults, cryptographic parameters, UI theme colors.
- **`app/protocol.py`:** 4-byte big-endian framing (`!I`) preventing TCP fragmentation issues.
- **`app/database.py`:** Thread-safe SQLite connection pooling and query parameters.
- **`app/authentication.py`:** Argon2id/PBKDF2 validation, brute force rate limiting.
- **`app/encryption.py`:** AES-GCM cipher wrappers and SHA-256 streaming hashing.
- **`app/key_exchange.py`:** Curve25519 handshakes and session key mapping.
- **`app/server.py`:** Non-blocking multi-threaded TCP server routing blind frames.
- **`app/client.py`:** Background receiver loop and automatic heartbeat pinging.
- **`app/messaging.py`:** End-to-end encrypted chat state and message queuing.
- **`app/file_transfer.py`:** 64 KB chunk streaming, path sanitization, and verification.
- **`gui/` Package:** CustomTkinter dashboard, chat bubbles, progress indicators, server monitor.

---

## 12. Testing and Results
Automated unit and integration testing was executed with pytest. All 27 tests passed successfully.

| Test Scenario | Module | Tested Behavior | Status |
| :--- | :--- | :--- | :--- |
| **User Registration** | `test_auth.py` | Unique username creation & hash validation | **PASSED** |
| **Duplicate Prevention** | `test_auth.py` | Rejecting duplicate usernames | **PASSED** |
| **Password Rules** | `test_auth.py` | Min length, uppercase, digit requirements | **PASSED** |
| **Brute Force Defense** | `test_auth.py` | Rate limiting after 5 consecutive failures | **PASSED** |
| **AES-256-GCM** | `test_encryption.py`| Plaintext encryption & exact decryption | **PASSED** |
| **Unique Nonces** | `test_encryption.py`| Cryptographic nonces change per encryption | **PASSED** |
| **Tampered Ciphertext** | `test_encryption.py`| InvalidTag detected on modified ciphertext | **PASSED** |
| **Tampered Nonce** | `test_encryption.py`| InvalidTag detected on modified nonce | **PASSED** |
| **Wrong Key Rejection** | `test_encryption.py`| Rejection when decrypted with foreign key | **PASSED** |
| **X25519 Derivation** | `test_key_exchange.py`| Identical HKDF session keys on both peers | **PASSED** |
| **Protocol Framing** | `test_protocol.py` | 4-byte header packing and unpacking | **PASSED** |
| **Server Lifecycle** | `test_network.py` | Server startup, binding, and clean shutdown | **PASSED** |
| **TCP Client Auth** | `test_network.py` | Client login over socket with session token | **PASSED** |
| **Presence Broadcast** | `test_network.py` | Real-time user list update on connect/disconnect | **PASSED** |
| **Concurrent Clients**| `test_network.py` | 5 concurrent client sessions on single server | **PASSED** |
| **E2E Messaging** | `test_messaging.py` | Full roundtrip encrypted chat between 2 peers | **PASSED** |
| **Path Traversal** | `test_file_transfer.py`| Sanitizing `../../` and Windows backslashes | **PASSED** |
| **Chunked File Transfer**| `test_file_transfer.py`| Multi-chunk transfer with full SHA-256 match | **PASSED** |
| **Invalid File Catch** | `test_file_transfer.py`| Safe handling of missing file paths | **PASSED** |

---

## 13. Limitations
1. **Network Boundary:** Operates exclusively within the local subnet (LAN/WLAN) or VPN tunnel; does not traverse symmetric NATs without port forwarding.
2. **Metadata Visibility:** The relay server observes peer IP addresses and packet sizes (traffic analysis), although it has zero access to message or file contents.
3. **Offline Message Storage:** Messages sent to offline peers are held locally until the recipient reconnects.

---

## 14. Future Scope
1. **Signal Protocol Double Ratchet:** Integrate Diffie-Hellman ratcheting for continuous per-message forward secrecy.
2. **Group Messaging:** Extend X25519 pairwise keys to multi-party MLS (Messaging Layer Security) groups.
3. **Voice/Video Calling:** Implement real-time WebRTC/SRTP encrypted peer-to-peer audio and video streaming.
4. **mDNS / ZeroConf Discovery:** Implement automated peer discovery using Bonjour/Avahi without needing manual server IP entry.

---

## 15. Conclusion
The **Encrypted LAN Chat & File Sharing System** successfully meets all engineering and security specifications. By integrating AES-256-GCM, X25519 ephemeral key agreement, Argon2id password hashing, and chunked SHA-256 file verification into an intuitive CustomTkinter desktop interface, the project provides a battle-tested, secure, and privacy-preserving intranet communication platform for universities, enterprises, and research labs.

---

## 16. References
1. Dworkin, M. (2007). *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC*. NIST Special Publication 800-38D.
2. Langley, A., Hamburg, M., & Turner, S. (2016). *Elliptic Curves for Security: Curve25519 and Curve448*. RFC 7748.
3. Krawczyk, H., & Eronen, P. (2010). *HMAC-based Extract-and-Expand Key Derivation Function (HKDF)*. RFC 5869.
4. Biryukov, A., Dinu, D., & Khovratovich, A. (2016). *Argon2: New Generation of Memory-Hard Functions for Password Hashing*. Password Hashing Competition.
5. Python Software Foundation. (2024). *Socket Programming & Cryptography Hazmat Documentation*.
