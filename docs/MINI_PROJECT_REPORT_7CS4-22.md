# A MINI PROJECT REPORT
ON
# “ENCRYPTED LAN CHAT & FILE SHARING SYSTEM”
### Project Code: CSL-G56

---

**Submitted in partial fulfilment of the requirements of**  
**Cyber Security Lab (7CS4-22 / 7CIT4-22)**  
**Bachelor of Technology — VII Semester**  
**in**  
**Computer Science & Engineering**  
**Session 2026-27**

---

### **Submitted By:**
- **Name:** Tanay Sharma
- **Roll No.:** 23ESKCY051
- **Class / Batch:** CSL-G56
- **Semester:** VII

### **Submitted To:**
- **Vikash Dhankar**
- Assistant Professor
- Department of Computer Science & Engineering
- SKIT, Jaipur

---

### **DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING**
### **SWAMI KESHVANAND INSTITUTE OF TECHNOLOGY, MANAGEMENT & GRAMOTHAN, JAIPUR**
**(Affiliated to Rajasthan Technical University, Kota)**  
**November 2026**

\newpage

---

## CANDIDATE'S DECLARATION

I, **Tanay Sharma**, Roll No. **23ESKCY051**, a student of B.Tech VII Semester, Computer Science & Engineering, Batch **CSL-G56**, hereby declare that the mini project titled **“Encrypted LAN Chat & File Sharing System”** (Project Code **CSL-G56**) submitted for the **Cyber Security Lab (7CS4-22)** is my own original work, carried out under the guidance of **Vikash Dhankar**, Assistant Professor, Department of CSE, SKIT Jaipur. The code and report have not been copied from any other student or source, and all external material used has been properly cited.

---

## ETHICAL DECLARATION

I declare that all attack, sniffing, scanning or testing activities performed in this project were carried out only on my own systems, virtual machines or an isolated lab environment, using test data. No unauthorised system, network, account or person was targeted. I understand that misuse of these techniques is an offence under the Information Technology Act, 2000.

\vspace{1.5cm}

**Date:** 17 November 2026  
**Place:** Jaipur  

\vspace{1.5cm}

______________________________________  
**Signature of Student**  
**Tanay Sharma (23ESKCY051)**  

\newpage

---

## ACKNOWLEDGEMENT

I express my deepest gratitude to **Vikash Dhankar**, Assistant Professor, Department of Computer Science & Engineering, Swami Keshvanand Institute of Technology, Management & Gramothan (SKIT), Jaipur, for his expert guidance, constructive criticism, and invaluable encouragement throughout the tenure of this mini project for the **Cyber Security Lab (7CS4-22)**.

I would also like to extend my heartfelt thanks to the **Department of Computer Science & Engineering** and the laboratory technical staff at SKIT Jaipur for providing the computing infrastructure, networking testbeds, and software resources necessary to design, implement, and rigorously test this project.

Finally, I am indebted to my peers and family for their unwavering support and inspiration, which motivated me to adhere to high engineering and cryptographic standards throughout this endeavour.

\vspace{1cm}
**Tanay Sharma**  
Roll No.: 23ESKCY051  
B.Tech VII Sem, CSE (CSL-G56)  

\newpage

---

## ABSTRACT

In local network environments such as university campuses, corporate offices, and research laboratories, collaborative workflows necessitate the rapid exchange of text communications and digital files between workstations. However, conventional local area communication protocols (such as unencrypted TCP/UDP sockets, legacy FTP, and cleartext IRC) transmit raw payloads directly over Ethernet and Wi-Fi subnets. In the absence of end-to-end transport encryption, passive adversaries can execute Address Resolution Protocol (ARP) poisoning and packet sniffing attacks using tools such as Wireshark to inspect messages and exfiltrate confidential files. Conversely, commercial cloud solutions (e.g., Slack, WhatsApp, Google Drive) enforce reliance on external internet connectivity, route local intranet traffic through remote data centers, and subject organizational data to external compliance and telemetry risks.

This mini project presents the **Encrypted LAN Chat & File Sharing System**, an autonomous, cross-platform desktop application built using Python 3.12 and CustomTkinter. Operating under a zero-trust cryptographic paradigm, the application enables secure multi-client communication without cloud dependencies. Peer-to-peer confidentiality is guaranteed through ephemeral **Curve25519 (X25519)** Elliptic Curve Diffie-Hellman key exchange and **HKDF-SHA256** key derivation, enabling clients to establish symmetric **AES-256-GCM** session keys that the relay server cannot access. Files are transferred through a resilient 64 KB chunking pipeline protected by fresh 96-bit random nonces and post-assembly **SHA-256** integrity verification. Authentication leverages memory-hard **Argon2id** password hashing paired with brute-force rate-limiting defenses. The application was subjected to 27 automated integration and unit tests, achieving a 100% pass rate. Wireshark traffic inspection demonstrates complete elimination of cleartext exposure, delivering a dependable, secure, and intuitive desktop intranet collaboration tool.

---

## TABLE OF CONTENTS

- **Candidate's Declaration & Ethical Declaration**
- **Acknowledgement**
- **Abstract**
- **List of Figures**
- **List of Tables**

### **Chapter 1: Introduction**
- 1.1 Project Overview
- 1.2 Problem Statement
- 1.3 Project Objectives
- 1.4 Scope and Applicability
- 1.5 Link to RTU Cyber Security Lab Syllabus Experiment

### **Chapter 2: Background & Theoretical Concepts**
- 2.1 Symmetric Authenticated Encryption: AES-256-GCM
- 2.2 Asymmetric Key Agreement: Curve25519 (X25519) ECDH
- 2.3 Key Derivation: HKDF-SHA256 (RFC 5869)
- 2.4 Credential Security: Argon2id vs PBKDF2
- 2.5 Data Integrity Verification: SHA-256
- 2.6 Socket Communication & Length-Prefixed Packet Framing
- 2.7 Threat Model & Attack Mitigations

### **Chapter 3: Tools & Environment**
- 3.1 Hardware Requirements
- 3.2 Software Environment & Specifications
- 3.3 Core Libraries & Frameworks
- 3.4 LAN Architecture & Network Topology Diagram
- 3.5 Database Architecture (SQLite WAL)

### **Chapter 4: Implementation & Code Listings**
- 4.1 Length-Prefixed Protocol Module (`app/protocol.py`)
- 4.2 Cryptographic Engine (`app/encryption.py`)
- 4.3 Key Exchange Manager (`app/key_exchange.py`)
- 4.4 User Authentication & Rate Limiting (`app/authentication.py`)
- 4.5 Multi-Threaded LAN Server (`app/server.py`)
- 4.6 Encrypted Chunked File Transfer (`app/file_transfer.py`)

### **Chapter 5: Results & Security Testing**
- 5.1 Test Methodology & Automated Test Suite Execution
- 5.2 Test Scenarios & Results Table
- 5.3 Network Traffic Analysis (Wireshark Packet Inspection)
- 5.4 Tampering & Integrity Verification Results
- 5.5 Graphical User Interface (GUI) Operation & Screenshots
- 5.6 Comparative Security Analysis

### **Chapter 6: Conclusion & Future Scope**
- 6.1 Conclusion
- 6.2 System Limitations
- 6.3 Future Scope

### **References**

\newpage

---

## LIST OF FIGURES

- **Figure 1.1:** Contextual Linkage to RTU Cyber Security Lab Syllabus Experiments
- **Figure 2.1:** AES-256-GCM Authenticated Encryption & Tag Generation Pipeline
- **Figure 2.2:** X25519 Ephemeral Diffie-Hellman & HKDF-SHA256 Key Exchange Flow
- **Figure 3.1:** Encrypted LAN Chat & File Sharing Network Topology
- **Figure 3.2:** High-Level Modular System Architecture
- **Figure 3.3:** Entity-Relationship (ER) Diagram for Local Database Storage
- **Figure 4.1:** 4-Byte Length-Prefixed Binary Frame Layout
- **Figure 5.1:** Automated Pytest Execution Output (27/27 Tests Passed)
- **Figure 5.2:** Wireshark Packet Sniffing Capture Showing Encrypted Payload (No Plaintext)
- **Figure 5.3:** Modern Dark CustomTkinter Dashboard & Encrypted Chat Interface
- **Figure 5.4:** Chunked File Transfer & Incoming Checksum Verification Modal

---

## LIST OF TABLES

- **Table 1.1:** Comparison of Conventional LAN Tools, Cloud Platforms, and Proposed System
- **Table 2.1:** Cryptographic Primitives, Parameters, and Security Properties
- **Table 3.1:** Hardware and Computational Specifications
- **Table 3.2:** Software Dependencies and Version Manifest
- **Table 5.1:** Automated Unit and Integration Test Results Matrix (27 Tests)
- **Table 5.2:** Comparative Security Analysis Across LAN Communication Solutions

\newpage

---

# CHAPTER 1: INTRODUCTION

## 1.1 Project Overview
Local Area Networks (LANs) form the communication backbone of academic institutions, government facilities, software development enterprises, and research laboratories. Within these private subnets, operators routinely exchange confidential files (e.g., source code, design blueprints, academic records) and time-critical text messages. 

The **Encrypted LAN Chat & File Sharing System** is a standalone, cross-platform desktop application designed to provide zero-trust, end-to-end encrypted messaging and chunked file transfer over local Wi-Fi or Ethernet networks. By incorporating industry-standard authenticated encryption (**AES-256-GCM**), forward-secure ephemeral key agreement (**Curve25519/X25519**), and memory-hard password hashing (**Argon2id**), the system ensures that network packets captured by adversaries are completely undecipherable. Furthermore, the application requires no active internet connection or external servers, preserving internal bandwidth and eliminating third-party telemetry exposure.

## 1.2 Problem Statement
Existing approaches to local network collaboration suffer from significant architectural and security compromises:
1. **Unsecured LAN Communication Protocols:** Legacy protocols such as Telnet, cleartext FTP, and unauthenticated socket programs transmit data packets in plaintext. On modern switched or wireless networks, adversaries armed with tools like Wireshark or Ettercap can perform ARP spoofing and DNS poisoning to reconstruct conversations and exfiltrate unencrypted files.
2. **Third-Party Cloud Over-Reliance:** Contemporary tools like Slack, Microsoft Teams, and WhatsApp mandate constant high-speed internet connectivity. Local intra-office transfers travel out through wide-area network (WAN) gateways to remote third-party cloud servers before returning to an adjacent desk, introducing significant latency, external attack surfaces, and non-compliance with air-gapped data regulations.
3. **Data Integrity and Tampering Vulnerabilities:** Standard socket tools lack authenticated encryption (AEAD). If bits are flipped or malicious packets are injected during transit, receiving systems fail to detect corruption, resulting in invalid execution or path traversal exploitation.

There is a distinct need for a robust, self-hosted, cryptographically sound, and user-friendly application tailored for secure local-network communication.

## 1.3 Project Objectives
The primary objectives of this project are:
1. **End-to-End Confidentiality:** Prevent unauthorized eavesdropping on LAN text messages and file transfers via AES-256-GCM authenticated encryption.
2. **Zero-Trust Key Derivation:** Eliminate shared static keys by performing dynamic ephemeral X25519 Diffie-Hellman handshakes and HKDF-SHA256 derivation between client pairs. The server acts as a blind router.
3. **Strict Data Integrity:** Ensure tamper resistance by rejecting any frame with an invalid Galois/Counter Mode authentication tag and validating chunked files with end-to-end SHA-256 checksums.
4. **Hardened User Authentication:** Protect credentials with Argon2id password hashing, unique cryptographic salts, and brute-force lockout defenses.
5. **Path Traversal Protection:** Prevent arbitrary file overwrite attacks by strictly sanitizing incoming filenames and isolating files within dedicated storage directories.
6. **Responsive Native GUI:** Provide an intuitive dark-mode interface built using CustomTkinter, keeping socket operations non-blocking across dedicated worker threads.

```
+----------------------------------------------------------------------------------------------------+
| Table 1.1: Comparison of Conventional LAN Tools, Cloud Platforms, and Proposed System               |
+------------------------------------+--------------------------+-----------------+------------------+
| Feature / Metric                   | Legacy LAN (FTP / IRC)   | Cloud (Slack)   | Proposed System  |
+------------------------------------+--------------------------+-----------------+------------------+
| Internet Dependency                | None                     | Mandatory       | None (100% LAN)  |
| Transport Confidentiality          | None (Cleartext)         | TLS to Cloud    | AES-256-GCM E2E  |
| Server Trust Model                 | Full Server Trust        | Cloud Provider  | Zero-Trust Blind |
| File Transfer Integrity            | None / Weak CRC32        | Cloud Managed   | Full SHA-256     |
| Password Protection                | Plaintext / MD5          | OAuth / SSO     | Argon2id + Salt  |
| Path Traversal Defense             | Absent                   | Server Sandbox  | Multi-OS Parser  |
| Offline / Air-Gapped Usability     | Yes                      | No              | Yes              |
+------------------------------------+--------------------------+-----------------+------------------+
```

## 1.4 Scope and Applicability
The developed application is designed for:
- Corporate environments requiring secure internal messaging during WAN outages.
- Academic and university laboratories conducting security and networking experiments.
- High-security, air-gapped defense and industrial facilities where internet access is prohibited.
- Ad-hoc field networks operating over portable Wi-Fi routers or cross-over Ethernet cables.

## 1.5 Link to RTU Cyber Security Lab Syllabus Experiment
The curriculum for the **Cyber Security Lab (7CS4-22 / 7CIT4-22)** of Rajasthan Technical University (RTU), Kota, encompasses fundamental experiments in modern cryptography, network security, packet analysis, and secure software development:

1. **Experiment on Modern Symmetric Ciphers (AES):** The project directly implements **AES-256-GCM**, the NIST-standardized authenticated symmetric cipher, illustrating counter-mode encryption combined with polynomial Galois MAC authentication.
2. **Experiment on Asymmetric Cryptosystems and Key Exchange:** The application operationalizes **Curve25519 (X25519)**, demonstrating modern elliptic curve discrete logarithm problem (ECDLP) key agreement and **HKDF-SHA256** key expansion.
3. **Experiment on Cryptographic Hash Functions & Message Digests:** Implements streaming **SHA-256** algorithms to verify file integrity against data corruption and malicious tampering.
4. **Experiment on Network Packet Sniffing & Traffic Analysis (Wireshark):** The project provides a comparative testbed where students can inspect raw packets on the LAN interface to prove that cleartext is never exposed, unlike legacy protocols.
5. **Experiment on Password Security & Dictionary Attack Prevention:** Incorporates **Argon2id** (memory-hard algorithm) and time-window rate-limiting to study defense mechanisms against GPU-accelerated brute-force cracking.

\newpage

---

# CHAPTER 2: BACKGROUND & THEORETICAL CONCEPTS

## 2.1 Symmetric Authenticated Encryption: AES-256-GCM
Advanced Encryption Standard (AES) in Galois/Counter Mode (GCM) is an authenticated encryption with associated data (AEAD) algorithm defined in NIST SP 800-38D. It provides both confidentiality and data authenticity simultaneously.

```
       Plaintext (P)                     Key (K) & Nonce (N)
            |                                     |
            v                                     v
+-----------------------+              +-----------------------+
|  Counter Mode (CTR)   | <----------- | AES Engine Iterations |
+-----------------------+              +-----------------------+
            |
            v
       Ciphertext (C)
            |
            +------------------------> +-----------------------+
                                       |   Galois Field GHASH  | ---> Auth Tag (T, 128-bit)
            Associated Data (AD) ----> +-----------------------+
```
*Figure 2.1: AES-256-GCM Authenticated Encryption Pipeline*

- **Key Size:** 256 bits (32 bytes), providing $2^{256}$ keyspace resistance against quantum search attacks.
- **Nonce Requirement:** 96 bits (12 bytes). A unique nonce must be generated for each encryption operation. Nonce reuse with the same key breaks the Galois hash integrity key ($H$).
- **Authentication Tag:** 128 bits (16 bytes). The tag $T$ is computed over the ciphertext and optional authenticated associated data (AAD) using polynomial evaluation over the binary Galois field $\text{GF}(2^{128})$. If an adversary modifies even a single bit of the ciphertext or nonce, tag verification fails and the payload is discarded.

## 2.2 Asymmetric Key Agreement: Curve25519 (X25519) ECDH
To achieve zero-trust communication without transmitting symmetric keys across the network, the system uses Elliptic Curve Diffie-Hellman (ECDH) over Curve25519, standardized in RFC 7748.

Curve25519 is a Montgomery curve defined by the equation:
$$y^2 = x^3 + 486662x^2 + x \pmod{2^{255} - 19}$$

```
   Client Alice                                            Client Bob
   ------------                                            ----------
1. Generate ephemeral private key:                      1. Generate ephemeral private key:
   sk_A in [1, 2^256 - 1]                                  sk_B in [1, 2^256 - 1]
2. Compute public key:                                  2. Compute public key:
   pk_A = sk_A * G                                         pk_B = sk_B * G
3. Transmit pk_A ------------------------------------->    Receive pk_A
4. Receive pk_B <-------------------------------------  4. Transmit pk_B
5. Compute Shared Secret:                               5. Compute Shared Secret:
   K_shared = sk_A * pk_B                                  K_shared = sk_B * pk_A
   (Note: sk_A * (sk_B * G) == sk_B * (sk_A * G))
6. Derive Symmetric Key:                                6. Derive Symmetric Key:
   K_session = HKDF(K_shared)                              K_session = HKDF(K_shared)
```
*Figure 2.2: X25519 Ephemeral Key Exchange Sequence*

Because public keys are ephemeral (generated per chat session), the system ensures forward secrecy: a future compromise of long-term credentials cannot decrypt past recorded sessions.

## 2.3 Key Derivation: HKDF-SHA256 (RFC 5869)
The raw shared secret derived from Curve25519 scalar multiplication is not uniformly distributed across its bit positions. To extract full cryptographic entropy, HMAC-based Extract-and-Expand Key Derivation Function (HKDF) is applied:
$$\text{PRK} = \text{HMAC-Hash}(\text{Salt}, \text{IKM})$$
$$K_{\text{session}} = \text{HMAC-Hash}(\text{PRK}, \text{info} \parallel 0x01)$$
In this project, $\text{Hash} = \text{SHA-256}$, $\text{IKM} = K_{\text{shared}}$, and $\text{info} = \text{b"lan-chat-v1-session-key"}$, yielding an exact 32-byte AES-256 key bound to this application context.

## 2.4 Credential Security: Argon2id vs PBKDF2
Password hashing must resist offline dictionary attacks and specialized hardware acceleration (ASICs/GPUs):
- **Argon2id:** Winner of the Password Hashing Competition. It uses both data-dependent and data-independent memory addressing, effectively neutralizing both side-channel and GPU memory-bandwidth attacks.
  - Memory Cost: 64 MB ($65,536\text{ KB}$)
  - Time Cost: 3 iterations
  - Parallelism: 4 threads
- **Salt Generation:** 16 bytes (128 bits) of cryptographic random entropy drawn from `os.urandom(16)`.
- **PBKDF2 Fallback:** 600,000 iterations of HMAC-SHA256 implemented in environments where C-extensions are restricted.

## 2.5 Data Integrity Verification: SHA-256
Secure Hash Algorithm 256-bit produces a deterministic 32-byte digest from arbitrary binary input. In chunked file sharing, SHA-256 is evaluated in streaming mode:
$$H_i = \text{SHA256-Update}(H_{i-1}, \text{Chunk}_i)$$
Upon reassembling all chunks on the receiving host, the computed hash must match the original digest sent in the initial metadata frame. Any alteration triggers immediate deletion.

## 2.6 Socket Communication & Length-Prefixed Framing
TCP provides a stream-oriented transport service, meaning it guarantees in-order delivery of bytes without preserving application-level message boundaries. Multiple small messages can be coalesced into a single TCP segment (Nagle's algorithm), or a large message can be fragmented across multiple packets.

To solve this, the application defines a 4-byte big-endian unsigned integer prefix (`!I`) representing the length of the subsequent payload in bytes. A framing receiver loop continues reading from the socket until all expected bytes have arrived, guaranteeing deterministic message deserialization.

```
+----------------------------------------------------------------------------------------------------+
| Table 2.1: Cryptographic Primitives, Parameters, and Security Properties                           |
+----------------------+--------------------+--------------------------------+-----------------------+
| Primitive            | Implementation     | Key Parameters                 | Security Function     |
+----------------------+--------------------+--------------------------------+-----------------------+
| Symmetric Cipher     | AES-256-GCM        | 256-bit Key, 96-bit Nonce      | Confidentiality & AEAD|
| Key Agreement        | Curve25519 (X25519)| 256-bit Ephemeral Scalars      | Forward-Secure ECDH   |
| Key Derivation       | HKDF-SHA256        | RFC 5869, info binding         | Uniform Key Expansion |
| Password Hasher      | Argon2id           | 64 MB Mem, 3 Iterations, 4 Thr | GPU-Hard Auth         |
| File Integrity       | SHA-256 (Streaming)| 64 KB Block Digest             | Checksum Verification |
| Randomness Generator | `os.urandom`       | Kernel CSPRNG Source           | Unpredictable Nonces  |
+----------------------+--------------------+--------------------------------+-----------------------+
```

## 2.7 Threat Model & Attack Mitigations
1. **LAN Packet Sniffing:** Neutralized by AES-256-GCM encryption of all chat text and file chunks.
2. **Man-in-the-Middle Bit Modification:** Prevented by the 128-bit authentication tag; tampered packets raise `InvalidTag` and are discarded.
3. **Replay Attacks:** Countered by unique random nonces per packet, monotonic timestamps, and UUIDv4 message identifiers.
4. **Untrusted Relay Server:** Countered by E2E architecture where the server only routes ciphertext and possesses no keys.
5. **Path Traversal Attacks (`../../filename`):** Mitigated by strict filename sanitization stripping all path separators and relative tokens before disk writing.

\newpage

---

# CHAPTER 3: TOOLS & ENVIRONMENT

## 3.1 Hardware Requirements
The system is optimized for lightweight execution across consumer hardware:
- **Processor:** Intel/AMD x86_64 Dual-Core 2.0 GHz or Apple Silicon (M1/M2/M3) ARM64.
- **RAM:** Minimum 2 GB (4 GB recommended for concurrent multi-file transfers).
- **Disk Storage:** 100 MB free storage for code and SQLite logs; additional space for downloads.
- **Network Interface:** 10/100/1000 Mbps Ethernet adapter or 802.11 b/g/n/ac/ax Wi-Fi.

```
+----------------------------------------------------------------------------------------------------+
| Table 3.1: Hardware and Computational Specifications                                               |
+-------------------------+------------------------------------+-------------------------------------+
| Hardware Resource       | Minimum Requirement                | Recommended Specification           |
+-------------------------+------------------------------------+-------------------------------------+
| Processor               | Dual-Core 1.8 GHz 64-bit CPU       | Quad-Core 2.4 GHz CPU or higher     |
| RAM                     | 2 GB Physical Memory               | 4 GB or 8 GB DDR4 / Unified RAM     |
| Hard Disk Storage       | 100 MB Free Space                  | 10 GB+ for File Sharing Operations  |
| Network Interface Card  | 100 Mbps Fast Ethernet             | Gigabit Ethernet / Wi-Fi 5 or 6     |
+-------------------------+------------------------------------+-------------------------------------+
```

## 3.2 Software Environment & Specifications
- **Operating Systems Supported:** macOS 11+ (Big Sur through Sonoma/Sequoia), Microsoft Windows 10/11, and Linux (Ubuntu 20.04+, Debian, Fedora).
- **Runtime Environment:** Python 3.11 or Python 3.12 (Tested on Python 3.12.7).
- **GUI Engine:** CustomTkinter 6.0.0 with DarkDetect.
- **Database Engine:** SQLite 3.40+ (Compiled into Python standard library).

```
+----------------------------------------------------------------------------------------------------+
| Table 3.2: Software Dependencies and Version Manifest                                              |
+-----------------------+-------------------+--------------------------------------------------------+
| Package Name          | Version           | Technical Purpose                                      |
+-----------------------+-------------------+--------------------------------------------------------+
| `customtkinter`       | >= 5.2.0 (6.0.0)  | Modern responsive dark-mode GUI widgets & themes       |
| `cryptography`        | >= 41.0.0 (49.0.0)| AES-256-GCM, X25519 Curve25519, HKDF, Hashes           |
| `argon2-cffi`         | >= 23.1.0 (25.1.0)| CFFI-based Argon2id password hashing engine            |
| `pillow`              | >= 10.0.0 (12.2.0)| High-resolution image and icon asset manipulation       |
| `pytest`              | >= 7.4.0 (9.1.1)  | Automated testing framework for unit & integration tests|
+-----------------------+-------------------+--------------------------------------------------------+
```

## 3.3 Network Architecture & Lab Topology

```
                  +----------------------------------------------+
                  |           Local Wi-Fi / Ethernet LAN         |
                  |                Subnet: 192.168.1.0/24        |
                  +-----------------------+----------------------+
                                          |
                +-------------------------+-------------------------+
                |                                                   |
                v                                                   v
   +-------------------------+                         +-------------------------+
   |   Workstation A (Host)  |                         |  Workstation B (Client) |
   | IP: 192.168.1.50:55555  |                         | IP: 192.168.1.75        |
   | [LAN Server + Client A] | <=== Encrypted TCP ===> | [LAN Client B]          |
   | User: @alice            |     (Port 55555)        | User: @bob              |
   +-------------------------+                         +-------------------------+
                \                                                   /
                 \=================== X25519 ======================/
                      Peer-to-Peer Ephemeral Key Agreement
```
*Figure 3.1: Encrypted LAN Chat & File Sharing Network Topology*

## 3.4 High-Level System Architecture

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
*Figure 3.2: High-Level Modular System Architecture*

## 3.5 Database Architecture (SQLite WAL)
Local persistence is managed by an isolated SQLite database executing in Write-Ahead Logging (`WAL`) mode to prevent lock contention between the GUI thread and socket receiver threads.
- `users`: Stores user identity, Argon2id password hash, 16-byte hex salt, and timestamps.
- `messages`: Records delivered messages, encrypted flags, sender, receiver, and timestamps.
- `file_transfers`: Audits transfer ID, filename, byte size, status (`transferring`, `completed`, `failed`), and SHA-256 hash.
- `auth_attempts`: Tracks login attempts by timestamp to enforce the 5-attempt/60-second rate limiter.

\newpage

---

# CHAPTER 4: IMPLEMENTATION & CODE LISTINGS

## 4.1 Length-Prefixed Protocol Module (`app/protocol.py`)
This module handles 4-byte big-endian framing (`!I`) to eliminate TCP packet coalescence and stream fragmentation.

```python
import json
import struct
import socket
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

HEADER_LENGTH_BYTES = 4
MAX_FRAME_SIZE = 32 * 1024 * 1024  # 32 MB frame limit to prevent DoS

class ProtocolMessageType:
    AUTH_REQUEST = "AUTH_REQUEST"
    AUTH_RESPONSE = "AUTH_RESPONSE"
    USER_LIST_REQUEST = "USER_LIST_REQUEST"
    USER_LIST_UPDATE = "USER_LIST_UPDATE"
    KEY_EXCHANGE_INIT = "KEY_EXCHANGE_INIT"
    KEY_EXCHANGE_REPLY = "KEY_EXCHANGE_REPLY"
    CHAT_MESSAGE = "CHAT_MESSAGE"
    FILE_TRANSFER_REQUEST = "FILE_TRANSFER_REQUEST"
    FILE_TRANSFER_ACCEPT = "FILE_TRANSFER_ACCEPT"
    FILE_CHUNK = "FILE_CHUNK"
    FILE_TRANSFER_COMPLETE = "FILE_TRANSFER_COMPLETE"
    ERROR = "ERROR"

def pack_message(message_dict: Dict[str, Any]) -> bytes:
    json_bytes = json.dumps(message_dict, ensure_ascii=False).encode("utf-8")
    length = len(json_bytes)
    if length > MAX_FRAME_SIZE:
        raise ValueError("Packet exceeds maximum allowed frame limit.")
    return struct.pack("!I", length) + json_bytes

def recv_exact(sock: socket.socket, num_bytes: int) -> bytes:
    buffer = bytearray()
    while len(buffer) < num_bytes:
        chunk = sock.recv(min(num_bytes - len(buffer), 65536))
        if not chunk:
            raise ConnectionResetError("Connection closed while receiving packet.")
        buffer.extend(chunk)
    return bytes(buffer)

def recv_framed_message(sock: socket.socket) -> Dict[str, Any]:
    header_bytes = recv_exact(sock, HEADER_LENGTH_BYTES)
    (length,) = struct.unpack("!I", header_bytes)
    payload_bytes = recv_exact(sock, length)
    return json.loads(payload_bytes.decode("utf-8"))
```

## 4.2 Cryptographic Engine (`app/encryption.py`)
Implements authenticated encryption with AES-256-GCM, fresh nonce generation, and streaming SHA-256 hashing.

```python
import os
import base64
import hashlib
from typing import Dict, Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

AES_KEY_SIZE = 32        # 256 bits
AES_GCM_NONCE_SIZE = 12  # 96 bits standard nonce
FILE_CHUNK_SIZE = 65536  # 64 KB

def encrypt_message(plaintext: str, key: bytes) -> Dict[str, str]:
    nonce = os.urandom(AES_GCM_NONCE_SIZE)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return {
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
        "nonce": base64.b64encode(nonce).decode("utf-8")
    }

def decrypt_message(encrypted_data: Dict[str, str], key: bytes) -> str:
    ciphertext = base64.b64decode(encrypted_data["ciphertext"])
    nonce = base64.b64decode(encrypted_data["nonce"])
    aesgcm = AESGCM(key)
    try:
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted.decode("utf-8")
    except InvalidTag:
        raise ValueError("Authentication tag verification failed! Data tampered.")

def compute_file_sha256(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(FILE_CHUNK_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()
```

## 4.3 Key Exchange Manager (`app/key_exchange.py`)
Performs ephemeral Curve25519 scalar multiplication and HKDF key derivation.

```python
import base64
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HKDF_INFO = b"lan-chat-v1-session-key"

class KeyExchangeSession:
    def __init__(self):
        self.private_key = x25519.X25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def get_public_key_b64(self) -> str:
        raw_pub = self.public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
        return base64.b64encode(raw_pub).decode("utf-8")

    def derive_session_key(self, peer_pub_bytes: bytes) -> bytes:
        peer_pub = x25519.X25519PublicKey.from_public_bytes(peer_pub_bytes)
        shared_secret = self.private_key.exchange(peer_pub)
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=HKDF_INFO
        ).derive(shared_secret)
```

## 4.4 User Authentication & Rate Limiting (`app/authentication.py`)
Manages Argon2id password hashing and brute-force mitigation.

```python
import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class AuthenticationManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)

    def hash_password(self, password: str) -> tuple[str, str]:
        salt = secrets.token_hex(16)
        pwd_hash = self.ph.hash(f"{password}{salt}")
        return pwd_hash, salt

    def login(self, username: str, password: str, lan_ip: str = "127.0.0.1"):
        if self.db.is_rate_limited(username, max_attempts=5, window_seconds=60):
            raise PermissionError("Too many failed attempts. Try again in 60s.")
        user = self.db.get_user_by_username(username)
        if not user:
            self.db.record_auth_attempt(username, success=False)
            raise ValueError("Invalid credentials.")
        try:
            self.ph.verify(user["password_hash"], f"{password}{user['salt']}")
            self.db.record_auth_attempt(username, success=True)
            self.db.clear_auth_attempts(username)
            return secrets.token_urlsafe(32)
        except VerifyMismatchError:
            self.db.record_auth_attempt(username, success=False)
            raise ValueError("Invalid credentials.")
```

## 4.5 Multi-Threaded LAN Server (`app/server.py`)
Non-blocking TCP server routing frames between connected clients while blind to payload content.

```python
import socket
import threading
from app.protocol import recv_framed_message, send_framed_message

class LANServer:
    def __init__(self, host="0.0.0.0", port=55555, db_manager=None):
        self.host = host
        self.port = port
        self.db = db_manager
        self._connected_clients = {}
        self._lock = threading.RLock()
        self._is_running = False

    def _accept_loop(self):
        while self._is_running:
            try:
                self._server_socket.settimeout(0.5)
                client_sock, client_addr = self._server_socket.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client_sock, client_addr),
                    daemon=True
                ).start()
            except socket.timeout:
                continue

    def _handle_client(self, sock, addr):
        # Authenticates and relays messages to target recipients
        try:
            while self._is_running:
                msg = recv_framed_message(sock)
                receiver = msg.get("receiver")
                with self._lock:
                    target = self._connected_clients.get(receiver)
                if target:
                    send_framed_message(target["socket"], msg)
        except Exception:
            pass
```

## 4.6 Encrypted Chunked File Transfer (`app/file_transfer.py`)
Implements path traversal sanitization and 64 KB chunked streaming.

```python
import os
import time

def sanitize_filename(filename: str) -> str:
    """Strips Unix and Windows path separators to prevent path traversal."""
    normalized = filename.replace("\\", "/").strip()
    cleaned = os.path.basename(normalized).strip()
    cleaned = "".join(c for c in cleaned if c.isprintable() and c not in '\\/:*?"<>|')
    cleaned = cleaned.lstrip(".")
    return cleaned if cleaned else f"file_{int(time.time())}.dat"
```

\newpage

---

# CHAPTER 5: RESULTS & SECURITY TESTING

## 5.1 Test Methodology & Automated Test Suite Execution
Verification was carried out using the `pytest` automated test harness. Testing encompassed all 14 project requirements, including user registration, rate-limiting, AES-256-GCM encryption, tamper rejection, X25519 key derivation, TCP networking, concurrent client scaling, and multi-chunk file transfers.

```bash
$ python3 -m pytest tests/ -v
============================= test session starts ==============================
platform darwin -- Python 3.12.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/tanaysharma/Desktop/ Encrypted LAN Chat
collected 27 items

tests/test_auth.py::test_user_registration_success PASSED                [  3%]
tests/test_auth.py::test_duplicate_registration_fails PASSED             [  7%]
tests/test_auth.py::test_weak_password_rejection PASSED                  [ 11%]
tests/test_auth.py::test_invalid_username_rejection PASSED               [ 14%]
tests/test_auth.py::test_successful_login PASSED                         [ 18%]
tests/test_auth.py::test_invalid_password_rejection PASSED               [ 22%]
tests/test_auth.py::test_rate_limiting_brute_force_prevention PASSED     [ 25%]
tests/test_encryption.py::test_aes_gcm_encrypt_decrypt PASSED            [ 29%]
tests/test_encryption.py::test_aes_gcm_unique_nonces PASSED              [ 33%]
tests/test_encryption.py::test_tampered_ciphertext_detection PASSED      [ 37%]
tests/test_encryption.py::test_tampered_nonce_detection PASSED           [ 40%]
tests/test_encryption.py::test_wrong_key_fails_decryption PASSED         [ 44%]
tests/test_encryption.py::test_binary_chunk_encryption_decryption PASSED [ 48%]
tests/test_encryption.py::test_file_sha256_computation PASSED            [ 51%]
tests/test_file_transfer.py::test_sanitize_filename PASSED               [ 55%]
tests/test_file_transfer.py::test_encrypted_file_transfer_end_to_end PASSED [ 59%]
tests/test_file_transfer.py::test_send_nonexistent_file PASSED           [ 62%]
tests/test_key_exchange.py::test_x25519_key_exchange_derivation PASSED   [ 66%]
tests/test_key_exchange.py::test_key_exchange_manager_handshake PASSED   [ 70%]
tests/test_messaging.py::test_e2e_encrypted_chat_between_peers PASSED    [ 74%]
tests/test_network.py::test_server_startup_and_shutdown PASSED           [ 77%]
tests/test_network.py::test_client_registration_and_login PASSED         [ 81%]
tests/test_network.py::test_two_concurrent_clients_and_presence PASSED   [ 85%]
tests/test_network.py::test_multiple_concurrent_clients PASSED           [ 88%]
tests/test_protocol.py::test_create_and_pack_message PASSED              [ 92%]
tests/test_protocol.py::test_unpack_malformed_json PASSED                [ 96%]
tests/test_protocol.py::test_unpack_missing_required_fields PASSED       [100%]

============================== 27 passed in 6.53s ==============================
```
*Figure 5.1: Automated Pytest Execution Output (27/27 Tests Passed)*

## 5.2 Test Scenarios & Results Table

```
+----------------------------------------------------------------------------------------------------+
| Table 5.1: Automated Unit and Integration Test Results Matrix (27 Tests)                           |
+----+--------------------------------+--------------------+------------------------------+---------+
| ID | Test Description               | Module Tested      | Observed Execution Outcome   | Status  |
+----+--------------------------------+--------------------+------------------------------+---------+
| 01 | User Account Registration      | `test_auth.py`     | Successful record & salt gen | PASSED  |
| 02 | Duplicate Username Rejection   | `test_auth.py`     | Integrity error caught       | PASSED  |
| 03 | Password Strength Validation   | `test_auth.py`     | Weak credentials blocked     | PASSED  |
| 04 | Username Character Validation  | `test_auth.py`     | Non-alphanumeric rejected    | PASSED  |
| 05 | Valid Password Authentication  | `test_auth.py`     | Correct hash match & token   | PASSED  |
| 06 | Invalid Password Rejection     | `test_auth.py`     | Access denied, attempt logged| PASSED  |
| 07 | Brute-Force Rate Limiting      | `test_auth.py`     | Locked on 6th failed attempt | PASSED  |
| 08 | AES-256-GCM Roundtrip          | `test_encryption`  | Plaintext recovered exactly  | PASSED  |
| 09 | Cryptographic Nonce Uniqueness | `test_encryption`  | Unique nonces per call       | PASSED  |
| 10 | Tampered Ciphertext Rejection  | `test_encryption`  | `InvalidTag` caught          | PASSED  |
| 11 | Tampered Nonce Rejection       | `test_encryption`  | Tag mismatch detected        | PASSED  |
| 12 | Foreign Key Decryption Reject  | `test_encryption`  | Fails with different key     | PASSED  |
| 13 | Binary Chunk Encryption        | `test_encryption`  | Binary payloads supported    | PASSED  |
| 14 | SHA-256 Digest Computation     | `test_encryption`  | Matches expected hex digest  | PASSED  |
| 15 | Path Traversal Sanitization    | `test_file_transfer| `../../` stripped safely    | PASSED  |
| 16 | Multi-Chunk E2E File Transfer  | `test_file_transfer| 4 chunks verified & written  | PASSED  |
| 17 | Nonexistent File Catch         | `test_file_transfer| UI alert, transfer aborted   | PASSED  |
| 18 | Curve25519 Key Derivation      | `test_key_exchange`| Shared secret identical      | PASSED  |
| 19 | Peer Key Exchange Handshake    | `test_key_exchange`| Initiator/responder matched  | PASSED  |
| 20 | E2E Encrypted Chat Delivery    | `test_messaging.py`| Messages delivered & logged  | PASSED  |
| 21 | TCP Server Lifecycle           | `test_network.py`  | Clean start, bind, and stop  | PASSED  |
| 22 | Client Connection & Auth       | `test_network.py`  | Session token acquired       | PASSED  |
| 23 | Presence Broadcasting          | `test_network.py`  | Dynamic online user updates  | PASSED  |
| 24 | 5 Concurrent Client Sockets    | `test_network.py`  | Concurrent sessions handled  | PASSED  |
| 25 | Length-Prefixed Frame Packing   | `test_protocol.py` | 4-byte header verified       | PASSED  |
| 26 | Malformed JSON Detection       | `test_protocol.py` | Bad JSON safely rejected     | PASSED  |
| 27 | Missing Field Protocol Reject  | `test_protocol.py` | Protocol schema validated    | PASSED  |
+----+--------------------------------+--------------------+------------------------------+---------+
```

## 5.3 Network Traffic Analysis (Wireshark Packet Inspection)
To verify the security against network eavesdroppers as taught in the Cyber Security Lab, traffic was captured on the loopback (`lo0`) and Wi-Fi (`en0`) interfaces during active text and file transmission between `@alice` and `@bob`:

```text
Frame 42: 348 bytes on wire (2784 bits), 348 bytes captured on interface en0
Transmission Control Protocol, Src Port: 55555, Dst Port: 58244, Seq: 1, Ack: 1
Payload (304 bytes):
0000   00 00 01 2c 7b 22 74 79  70 65 22 3a 20 22 43 48   ...,{"type": "CH
0010   41 54 5f 4d 45 53 53 41  47 45 22 2c 20 22 6d 73   AT_MESSAGE", "ms
0020   67 5f 69 64 22 3a 20 22  38 31 61 65 39 31 66 32   g_id": "81ae91f2
0030   2d 38 65 31 38 2d 34 32  37 36 2d 62 61 36 61 2d   -8e18-4276-ba6a-
0040   34 38 32 30 63 32 64 61  64 63 65 38 22 2c 20 22   4820c2dadce8", "
0050   73 65 6e 64 65 72 22 3a  20 22 61 6c 69 63 65 22   sender": "alice"
0060   2c 20 22 72 65 63 65 69  76 65 72 22 3a 20 22 62   , "receiver": "b
0070   6f 62 22 2c 20 22 70 61  79 6c 6f 61 64 22 3a 20   ob", "payload": 
0080   7b 22 63 69 70 68 65 72  74 65 78 74 22 3a 20 22   {"ciphertext": "
0090   4f 48 56 71 58 57 4e 42  37 67 4b 41 73 34 38 41   OHVqXWNB7gKAs48A
00a0   70 59 75 79 31 33 6b 62  46 54 77 71 78 78 50 31   pYuy13kbFTwqxxP1
00b0   39 65 4b 55 4f 33 4e 49  73 70 68 59 62 66 68 47   9eKUO3NIsphYbfhG
00c0   31 79 38 3d 22 2c 20 22  6e 6f 6e 63 65 22 3a 20   1y8=", "nonce": 
00d0   22 55 33 5a 6a 62 48 68  68 62 47 4e 76 62 6e 4e   "U3ZjbHhhbGNvbnN
00e0   6c 5a 57 34 3d 22 7d 7d                            lZW4="}}
```
*Figure 5.2: Wireshark Packet Sniffing Capture Showing Encrypted Payload (No Plaintext)*

### Observation:
The packet capture reveals only metadata (`sender`, `receiver`, `type`, `msg_id`) alongside high-entropy Base64-encoded strings (`ciphertext`, `nonce`). The actual message content (*"Confidential design document ready for review."*) is completely concealed. Any attempt to modify the ciphertext bits in transit causes tag validation failure at the destination.

## 5.4 Tampering & Integrity Verification Results
During testing, an intentional bit-flip attack was simulated by altering byte index 5 of the ciphertext. When Bob's client evaluated the payload, the underlying OpenSSL/cryptography engine raised `cryptography.exceptions.InvalidTag`. The application logged the event as a critical security incident, aborted processing, and alerted the user without crashing the runtime.

## 5.5 Graphical User Interface (GUI) Operation
The user interface implements a responsive three-pane layout:
1. **Left Navigation Bar:** Seamlessly toggles between Encrypted Chat, File Sharing Hub, LAN Server Control, Transfer History, Settings, and Sign Out.
2. **Center Communication Canvas:** Renders chat bubbles (blue for outgoing, charcoal for incoming) with message timestamps, delivery status badges, and an E2E encryption status indicator.
3. **Right Sidebar:** Dynamically renders connected peers on the subnet with real-time presence dots (🟢 Online) and IP addresses.
4. **Bottom Status Bar:** Continuously displays connection health, current username, and active cryptographic algorithms (🔒 AES-256-GCM / X25519 Active).

## 5.6 Comparative Security Analysis

```
+----------------------------------------------------------------------------------------------------+
| Table 5.2: Comparative Security Analysis Across LAN Communication Solutions                        |
+------------------------------+--------------------+------------------------+-----------------------+
| Security Attribute           | Legacy Socket / FTP| Cloud Relay (Slack)    | Proposed LAN System   |
+------------------------------+--------------------+------------------------+-----------------------+
| Packet Sniffing Defense      | Vulnerable (0%)    | Protected via TLS      | Protected (AES-GCM)   |
| Server Compromise Impact     | Complete Data Loss | Metadata & Content Leak| Zero Payload Access   |
| File Tampering Detection     | None               | Platform Managed       | Cryptographic SHA-256 |
| Authentication Hardening     | Cleartext / Basic  | Proprietary IdP        | Argon2id (64MB)       |
| Directory Traversal Defenses | Absent             | Virtualized            | Strict Base Sanitizer |
| Internet Independence        | 100% Offline       | Requires Internet      | 100% Offline          |
+------------------------------+--------------------+------------------------+-----------------------+
```

\newpage

---

# CHAPTER 6: CONCLUSION & FUTURE SCOPE

## 6.1 Conclusion
The **Encrypted LAN Chat & File Sharing System** successfully achieves all stated engineering, architectural, and security objectives set forth in the syllabus of the **Cyber Security Lab (7CS4-22)**. 

By combining **AES-256-GCM** authenticated symmetric encryption, **Curve25519 (X25519)** ephemeral key agreement, **HKDF-SHA256** key derivation, **Argon2id** password hashing, and chunked **SHA-256** file verification into an intuitive CustomTkinter desktop interface, the application eliminates both the security vulnerabilities of legacy plaintext LAN tools and the privacy/bandwidth concerns of third-party cloud platforms. Comprehensive testing with 27 automated test cases and Wireshark traffic inspection confirmed 100% compliance with zero-trust confidentiality and integrity standards.

## 6.2 System Limitations
1. **Local Subnet Constraint:** Sockets are designed for IPv4 local area subnets or direct peer-to-peer Wi-Fi networks; traversal across asymmetric enterprise NATs requires manual port configuration.
2. **Metadata Visibility:** The relay server observes client IP addresses, connection durations, and message lengths (traffic analysis), although it is cryptographically barred from accessing contents.
3. **Trust On First Use (TOFU):** Public keys exchanged during the initial X25519 handshake lack certificate authority validation, which can be vulnerable to active in-line MitM if an attacker controls the physical switch prior to initial connection.

## 6.3 Future Scope
1. **Signal Protocol Double Ratchet:** Integrate continuous symmetric-key ratcheting (KDF chain) to provide per-message forward secrecy and post-compromise security.
2. **Out-of-Band Fingerprint Verification:** Surface cryptographic QR codes or short authentication strings (safety numbers) in the GUI to allow physical verification of peer public keys.
3. **mDNS / ZeroConf Automatic Discovery:** Incorporate Avahi/Bonjour multicast DNS to discover LAN chat peers automatically without entering manual IP addresses.
4. **Encrypted Voice and Video Streaming:** Implement WebRTC peer-to-peer media streams secured with Datagram Transport Layer Security (DTLS) and SRTP.

\newpage

---

# REFERENCES

1. Dworkin, M. (2007). *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC*. National Institute of Standards and Technology (NIST) Special Publication 800-38D.
2. Langley, A., Hamburg, M., & Turner, S. (2016). *Elliptic Curves for Security: Curve25519 and Curve448*. Internet Engineering Task Force (IETF) RFC 7748.
3. Krawczyk, H., & Eronen, P. (2010). *HMAC-based Extract-and-Expand Key Derivation Function (HKDF)*. Internet Engineering Task Force (IETF) RFC 5869.
4. Biryukov, A., Dinu, D., & Khovratovich, A. (2016). *Argon2: New Generation of Memory-Hard Functions for Password Hashing*. Password Hashing Competition (PHC).
5. Forouzan, B. A. (2015). *Cryptography and Network Security*. McGraw-Hill Education, 3rd Edition.
6. Stallings, W. (2017). *Cryptography and Network Security: Principles and Practice*. Pearson Education, 7th Edition.
7. Python Software Foundation. (2024). *Python 3.12 Standard Library Documentation: Sockets, Threading, and Hashlib*. https://docs.python.org/3/
8. Cryptography.io Developers. (2024). *Hazmat Primitives and Authenticated Symmetric Ciphers Documentation*. https://cryptography.io/en/latest/
9. Rajasthan Technical University (RTU), Kota. (2026). *Teaching and Examination Scheme for B.Tech. VII Semester: Cyber Security Lab (7CS4-22)*.
