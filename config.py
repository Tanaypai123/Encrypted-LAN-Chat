"""
Configuration settings for Encrypted LAN Chat & File Sharing System.
Student: Tanay Sharma (ID: 23ESKCY051)
Group: CSL-G56
"""

from pathlib import Path
import os
import socket

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_FILE = DATABASE_DIR / "lan_chat.db"
STORAGE_DIR = BASE_DIR / "storage"
DOWNLOADS_DIR = STORAGE_DIR / "downloads"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Application Information
APP_NAME = "Encrypted LAN Chat & File Sharing"
APP_VERSION = "1.0.0"
STUDENT_NAME = "Tanay Sharma"
STUDENT_ID = "23ESKCY051"
SUBJECT_CODE = "23ESKCY051"
PROJECT_GROUP = "CSL-G56"

# Network Defaults
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 55555
DEFAULT_CLIENT_CONNECT_PORT = 55555
SOCKET_TIMEOUT = 10.0
HEARTBEAT_INTERVAL = 15.0
SOCKET_BUFFER_SIZE = 65536  # 64 KB socket buffer
HEADER_LENGTH_BYTES = 4      # 4-byte big-endian length prefix (supports up to 4GB frames)

# File Transfer Defaults
FILE_CHUNK_SIZE = 64 * 1024  # 64 KB per encrypted chunk
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB limit

# Cryptographic Constants
AES_KEY_SIZE = 32           # 256 bits
AES_GCM_NONCE_SIZE = 12     # 96 bits standard nonce
AES_GCM_TAG_SIZE = 16       # 128 bits tag
HKDF_INFO = b"lan-chat-v1-session-key"

# Password Hashing Constants
ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536  # 64 MB
ARGON2_PARALLELISM = 4
PBKDF2_ITERATIONS = 600000

# Authentication & Security
AUTH_RATE_LIMIT_ATTEMPTS = 5
AUTH_RATE_LIMIT_WINDOW = 60  # seconds
SESSION_TIMEOUT = 86400      # 24 hours

# UI Theme & Colors (Modern Dark Palette)
THEME_MODE = "dark"
COLOR_PRIMARY = "#3B82F6"        # Vibrant Blue
COLOR_PRIMARY_HOVER = "#2563EB"
COLOR_ACCENT = "#8B5CF6"         # Violet / Purple
COLOR_ACCENT_HOVER = "#7C3AED"
COLOR_BG_DARK = "#0B0F19"        # Deep Charcoal / Navy Background
COLOR_CARD = "#111827"           # Card Container Background
COLOR_CARD_SECONDARY = "#1E293B" # Secondary Card Background
COLOR_INPUT_BG = "#1F2937"       # Form Input Background
COLOR_BORDER = "#374151"         # Subtle Border
COLOR_TEXT_PRIMARY = "#F9FAFB"   # White / Off-white text
COLOR_TEXT_MUTED = "#9CA3AF"     # Gray / Muted text
COLOR_SUCCESS = "#10B981"        # Emerald Green
COLOR_WARNING = "#F59E0B"        # Amber
COLOR_DANGER = "#EF4444"         # Rose Red

# Utility to get local LAN IP addresses
def get_local_ip() -> str:
    """Retrieve the primary local LAN IP address of this machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Does not actually send data; connects to arbitrary external IP to identify default route interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip
