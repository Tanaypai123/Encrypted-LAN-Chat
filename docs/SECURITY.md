# Security Architecture & Threat Model
## Encrypted LAN Chat & File Sharing System
**Author:** Tanay Sharma (23ESKCY051, CSL-G56)

---

## 1. Threat Model & Mitigations

### A. Network Eavesdropping & Packet Sniffing (Confidentiality)
- **Threat:** An adversary on the same Wi-Fi subnet runs packet capture tools (e.g., Wireshark, tcpdump) to capture packets traversing the switch or router.
- **Mitigation:** All message text and file chunks are encrypted with **AES-256-GCM** using keys negotiated via ephemeral **X25519 Diffie-Hellman**. Cleartext payload bytes are never transmitted across the network.

### B. Man-in-the-Middle (MitM) & Message Alteration (Integrity)
- **Threat:** An active attacker on the LAN modifies bytes in transit (bit-flipping attack) or injects forged packets.
- **Mitigation:** AES-256-GCM produces a 128-bit authentication tag ($T$) alongside the ciphertext. Any modification to ciphertext bytes or nonces results in an immediate `cryptography.exceptions.InvalidTag` exception. The receiving client drops the packet and triggers a `SECURITY ALERT` in the user interface.

### C. Replay Attacks
- **Threat:** An attacker records a previously encrypted packet and retransmits it to duplicate actions.
- **Mitigation:** Every protocol message includes a unique `msg_id` (UUIDv4), an ISO-8601 UTC timestamp, and every encryption operation utilizes a freshly generated 96-bit cryptographically secure random nonce.

### D. Server Compromise / Untrusted Relay
- **Threat:** A compromised server operator inspects relayed traffic or logs database records.
- **Mitigation:** End-to-end encryption ensures that symmetric keys are derived exclusively between the two communicating clients. The server only sees encrypted blobs (`ciphertext`, `nonce`, and recipient metadata) and is incapable of decrypting messages or inspecting file contents.

### E. Path Traversal & Malicious File Overwrites
- **Threat:** A malicious user sends a file with a relative path such as `../../etc/shadow` or `..\..\..\Windows\System32\cmd.exe` to overwrite system files on the receiver's machine.
- **Mitigation:** The receiver's `sanitize_filename` function strips all directory separators (both Unix `/` and Windows `\`), removes control characters, and enforces strict destination storage inside the dedicated `storage/downloads/` folder. Files are never automatically executed.

### F. Brute Force Credential Guessing
- **Threat:** Automated scripts repeatedly attempt dictionary passwords against user accounts.
- **Mitigation:** The authentication engine enforces rate limiting (maximum 5 failed attempts within 60 seconds per identifier). If exceeded, account authentication is locked for the remainder of the window. Password hashes use **Argon2id** (64 MB memory cost, 3 iterations, 4 parallelism lanes) to make offline cracking economically and computationally impractical.

---

## 2. Cryptographic Specifications Summary

| Layer | Standard / Algorithm | Parameters | Purpose |
| :--- | :--- | :--- | :--- |
| **Symmetric Cipher** | AES-256-GCM | 256-bit key, 96-bit nonce, 128-bit tag | Authenticated payload & chunk encryption |
| **Key Agreement** | Curve25519 (X25519) | 256-bit ephemeral scalar curve | Forward-secure peer session key establishment |
| **Key Derivation** | HKDF (RFC 5869) | HMAC-SHA256, info="lan-chat-v1-session-key" | Symmetric key extraction from shared secret |
| **Password Hashing** | Argon2id | Memory: 64 MB, Time: 3, Threads: 4 | GPU-resistant credential storage |
| **File Checksum** | SHA-256 | Streaming 64 KB chunk hash | End-to-end file integrity verification |
| **Randomness Source**| `os.urandom` / `secrets` | OS CSPRNG (`/dev/urandom` / `CryptGenRandom`) | Nonces, tokens, and ephemeral curve scalars |

---

## 3. Cryptographic Nonce Policy
AES-GCM security depends strictly on **never reusing a nonce with the same key**. Reusing a nonce allows an attacker to compute the XOR of plaintexts and recover the GHASH authentication key.
- In this application, nonces are **never sequential integers** and **never hardcoded**.
- A fresh 12-byte (96-bit) cryptographically secure random nonce is generated using `os.urandom(12)` for every single chat message and for each individual 64 KB file chunk.
- At 96 bits, the probability of a nonce collision under the birthday bound is negligible ($< 2^{-32}$ for millions of chunks per key).

---

## 4. Known Limitations & Recommendations
1. **Public Key Infrastructure (PKI) / Out-of-Band Verification:** Current key exchange relies on Trust On First Use (TOFU). In future revisions, out-of-band safety numbers or QR code fingerprint scanning should be added to guarantee protection against active MitM during the initial handshake.
2. **Traffic Analysis:** The relay server can observe packet timing and sizes, identifying who communicates with whom and when. Padding messages to fixed block sizes is recommended for high-threat environments.
