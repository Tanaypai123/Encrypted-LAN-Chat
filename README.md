# Encrypted LAN Chat & File Sharing System (GUI)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Cryptography](https://img.shields.io/badge/security-AES--256--GCM%20%7C%20X25519-green.svg)](https://cryptography.io)
[![GUI Framework](https://img.shields.io/badge/GUI-CustomTkinter-indigo.svg)](https://customtkinter.tomschimansky.com/)
[![Tests](https://img.shields.io/badge/tests-27%20passed-brightgreen.svg)]()

A modern, high-performance, and secure desktop application for real-time encrypted messaging and chunked file transfer across computers connected to the same Local Area Network (Wi-Fi or Ethernet).

---

### Project Information
- **Student Name:** Tanay Sharma
- **University ID:** 23ESKCY051
- **Subject Code:** 23ESKCY051
- **Project Group:** CSL-G56
- **Project Type:** Syllabus Project
- **Application Type:** GUI-based Desktop Application

---

## Key Features

1. **End-to-End Encryption (E2E):** Messages and files are encrypted using **AES-256-GCM** with fresh 96-bit random nonces for every message and chunk.
2. **Curve25519 (X25519) Key Agreement:** Peers dynamically establish symmetric session keys using ephemeral Diffie-Hellman and HKDF-SHA256. The relay server acts as a blind router and cannot inspect payload contents.
3. **Argon2id Password Hashing:** Secure credential protection using memory-hard Argon2id (with PBKDF2-HMAC-SHA256 fallback), salt randomization, and brute-force rate limiting.
4. **Resilient Chunked File Sharing:** Large files are streamed in 64 KB encrypted chunks with real-time transfer progress, speed tracking, and post-assembly **SHA-256 integrity verification**.
5. **Path Traversal Protection:** Cross-platform path sanitization ensures received files are strictly deposited in `storage/downloads/` and never auto-executed.
6. **Presence & User Discovery:** Real-time online users sidebar displaying LAN IP addresses and connection status.
7. **Integrated Server Manager:** Host a TCP relay server directly from the GUI or run a headless dedicated server via CLI.
8. **Modern Dark-Themed UI:** Built with CustomTkinter featuring clean typography, badges, and responsive layouts.

---

## Technology Stack

- **Language:** Python 3.11+ (Tested on Python 3.12.7)
- **GUI Framework:** CustomTkinter & Pillow
- **Networking:** Multi-threaded TCP Sockets with 4-byte length-prefixed framing
- **Cryptography:** `cryptography` library (`AESGCM`, `X25519`, `HKDF`, `SHA256`, `secrets`)
- **Authentication:** `argon2-cffi` & `hashlib`
- **Database:** SQLite with Write-Ahead Logging (`WAL`) mode

---

## Installation & Setup

### 1. Clone or Download the Repository
```bash
git clone https://github.com/Tanaypai123/Encrypted-LAN-Chat.git
cd "Encrypted LAN Chat"
```

### 2. Set Up Python Virtual Environment (Recommended)

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

*(Note for Linux users: ensure `python3-tk` is installed via `sudo apt install python3-tk` if not already present).*

---

## How to Run the Application

### Mode A: Launch the Complete Desktop GUI
```bash
python main.py
```
This opens the modern CustomTkinter interface. From here you can:
- Sign in with an existing account.
- Click **"Register Now"** to create a new user.
- Click **"Host Local Server on this Machine"** to start the local LAN relay.

---

### Mode B: Run in Dedicated Headless Server Mode (CLI)
You can run a dedicated relay server on any computer or server on your LAN:
```bash
python main.py --server --port 55555
```
Output:
```
============================================================
Encrypted LAN Chat Server - Dedicated Mode
Student: Tanay Sharma (23ESKCY051, CSL-G56)
============================================================
[+] Server successfully listening on 0.0.0.0:55555
[+] LAN IP: 192.168.1.100
[+] Press Ctrl+C to terminate server.
```

---

## Testing Across Two Computers on the Same LAN

1. **Identify the Server's LAN IP:**
   - On the computer running the server (Computer A), note the LAN IP displayed on the Server Manager screen (e.g. `192.168.1.50`).
2. **Configure Firewall (If Prompted):**
   - Ensure inbound TCP connections on port `55555` are allowed through the firewall.
     - **Windows:** Allow Python through Windows Defender Firewall when prompted, or add an Inbound Rule for TCP port 55555.
     - **macOS:** Click "Allow" when the incoming connections prompt appears.
     - **Linux:** Run `sudo ufw allow 55555/tcp`.
3. **Connect from Computer B:**
   - Launch `python main.py` on Computer B.
   - Enter Computer A's LAN IP (e.g. `192.168.1.50`) and Port `55555`.
   - Register or sign in.
4. **Chat & Share Files:**
   - Both users will immediately appear in each other's "Online Users" list.
   - Click a user to start an end-to-end encrypted chat.
   - Click **"Send File"** or the paperclip icon to transfer files securely.

---

## Testing Two Clients on a Single Computer (Demo Mode)

You can easily simulate two users on one computer:
1. Open Terminal 1:
   ```bash
   python main.py
   ```
   - Click **"Host Local Server on this Machine"** (or go to "LAN Server" tab and click "Start Server").
   - Click "Register Now" and register user: `alice` / `AlicePass123`.
   - Sign in as `alice` (Server IP: `127.0.0.1`, Port: `55555`).

2. Open Terminal 2:
   ```bash
   python main.py
   ```
   - Register user: `bob` / `BobPass123`.
   - Sign in as `bob` (Server IP: `127.0.0.1`, Port: `55555`).

3. **Verify Functionality:**
   - Alice sees `@bob` in the right sidebar with a green indicator.
   - Alice clicks `@bob` and sends: `"Hello Bob! This message is E2E encrypted."`
   - Bob receives the message instantly with decrypted text and timestamp.
   - Bob sends a file to Alice. Alice accepts the transfer modal.
   - Both progress bars track chunked transfer up to 100%.
   - Final SHA-256 is verified and the file is saved in `storage/downloads/`.

---

## Running Automated Unit & Integration Tests

The project includes an extensive automated test suite covering authentication, encryption, protocol framing, networking, messaging, and chunked file transfer.

Run the entire test suite:
```bash
pytest tests/ -v
```

Expected result:
```
tests/test_auth.py::test_user_registration_success PASSED
tests/test_auth.py::test_duplicate_registration_fails PASSED
tests/test_auth.py::test_weak_password_rejection PASSED
tests/test_auth.py::test_invalid_username_rejection PASSED
tests/test_auth.py::test_successful_login PASSED
tests/test_auth.py::test_invalid_password_rejection PASSED
tests/test_auth.py::test_rate_limiting_brute_force_prevention PASSED
tests/test_encryption.py::test_aes_gcm_encrypt_decrypt PASSED
tests/test_encryption.py::test_aes_gcm_unique_nonces PASSED
tests/test_encryption.py::test_tampered_ciphertext_detection PASSED
tests/test_encryption.py::test_tampered_nonce_detection PASSED
tests/test_encryption.py::test_wrong_key_fails_decryption PASSED
tests/test_encryption.py::test_binary_chunk_encryption_decryption PASSED
tests/test_encryption.py::test_file_sha256_computation PASSED
tests/test_file_transfer.py::test_sanitize_filename PASSED
tests/test_file_transfer.py::test_encrypted_file_transfer_end_to_end PASSED
tests/test_file_transfer.py::test_send_nonexistent_file PASSED
tests/test_key_exchange.py::test_x25519_key_exchange_derivation PASSED
tests/test_key_exchange.py::test_key_exchange_manager_handshake PASSED
tests/test_messaging.py::test_e2e_encrypted_chat_between_peers PASSED
tests/test_network.py::test_server_startup_and_shutdown PASSED
tests/test_network.py::test_client_registration_and_login PASSED
tests/test_network.py::test_two_concurrent_clients_and_presence PASSED
tests/test_network.py::test_multiple_concurrent_clients PASSED
tests/test_protocol.py::test_create_and_pack_message PASSED
tests/test_protocol.py::test_unpack_malformed_json PASSED
tests/test_protocol.py::test_unpack_missing_required_fields PASSED

============================== 27 passed in 6.53s ==============================
```

---

## Documentation Links

- [Complete College Project Report](docs/PROJECT_REPORT.md)
- [System Architecture Specification](docs/ARCHITECTURE.md)
- [Security Threat Model & Cryptographic Details](docs/SECURITY.md)

---

## License & Academic Disclaimer
Developed by **Tanay Sharma (23ESKCY051, CSL-G56)** as a university syllabus project. All cryptographic operations use standard, well-audited libraries (`cryptography`, `argon2-cffi`).
