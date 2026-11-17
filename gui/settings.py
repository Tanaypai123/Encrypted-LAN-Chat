"""
Settings and Security Configuration Interface View.
Allows changing downloads directory, updating password, and inspecting cryptographic parameters.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog
from typing import Optional

from config import (
    DOWNLOADS_DIR,
    STUDENT_NAME,
    STUDENT_ID,
    SUBJECT_CODE,
    PROJECT_GROUP,
    APP_NAME,
    APP_VERSION,
    COLOR_BG_DARK,
    COLOR_CARD,
    COLOR_CARD_SECONDARY,
    COLOR_INPUT_BG,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_ACCENT
)
from app.network_manager import NetworkManager

class SettingsView(ctk.CTkFrame):
    """Settings, User Profile & Security Configuration View."""

    def __init__(self, master, network_mgr: NetworkManager, **kwargs):
        super().__init__(master, fg_color=COLOR_BG_DARK, **kwargs)
        self.network_mgr = network_mgr
        self.current_downloads_path = str(DOWNLOADS_DIR)

        self._build_ui()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLOR_BG_DARK)
        scroll.pack(fill="both", expand=True, padx=25, pady=20)

        # Title
        header = ctk.CTkLabel(
            scroll,
            text="Application Settings & Security",
            font=("Helvetica", 22, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        header.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(
            scroll,
            text="Manage storage preferences, credentials, and inspect cryptographic specifications.",
            font=("Helvetica", 12),
            text_color=COLOR_TEXT_MUTED
        )
        sub.pack(anchor="w", pady=(0, 20))

        # --- Card 1: Storage & Downloads Directory ---
        store_card = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=12, border_width=1, border_color="#1E293B")
        store_card.pack(fill="x", pady=(0, 20))

        store_inner = ctk.CTkFrame(store_card, fg_color="transparent")
        store_inner.pack(fill="both", expand=True, padx=25, pady=20)

        s_title = ctk.CTkLabel(store_inner, text="📁 Storage & Downloads", font=("Helvetica", 16, "bold"), text_color=COLOR_TEXT_PRIMARY)
        s_title.pack(anchor="w", pady=(0, 10))

        desc = ctk.CTkLabel(store_inner, text="Location where decrypted incoming files are verified and saved:", font=("Helvetica", 11), text_color=COLOR_TEXT_MUTED)
        desc.pack(anchor="w", pady=(0, 8))

        row1 = ctk.CTkFrame(store_inner, fg_color="transparent")
        row1.pack(fill="x")

        self.path_entry = ctk.CTkEntry(
            row1,
            width=380,
            fg_color=COLOR_INPUT_BG,
            border_color="#374151"
        )
        self.path_entry.insert(0, self.current_downloads_path)
        self.path_entry.pack(side="left", padx=(0, 10))

        browse_btn = ctk.CTkButton(
            row1,
            text="Browse...",
            font=("Helvetica", 12),
            fg_color="#374151",
            hover_color="#4B5563",
            width=90,
            command=self._on_browse_downloads
        )
        browse_btn.pack(side="left")

        # --- Card 2: Password & Account Security ---
        pwd_card = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=12, border_width=1, border_color="#1E293B")
        pwd_card.pack(fill="x", pady=(0, 20))

        pwd_inner = ctk.CTkFrame(pwd_card, fg_color="transparent")
        pwd_inner.pack(fill="both", expand=True, padx=25, pady=20)

        p_title = ctk.CTkLabel(pwd_inner, text="🔑 Change Password", font=("Helvetica", 16, "bold"), text_color=COLOR_TEXT_PRIMARY)
        p_title.pack(anchor="w", pady=(0, 15))

        self.old_pwd_entry = ctk.CTkEntry(pwd_inner, placeholder_text="Current Password", show="•", width=320, fg_color=COLOR_INPUT_BG, border_color="#374151")
        self.old_pwd_entry.pack(anchor="w", pady=(0, 10))

        self.new_pwd_entry = ctk.CTkEntry(pwd_inner, placeholder_text="New Password (min 8 characters)", show="•", width=320, fg_color=COLOR_INPUT_BG, border_color="#374151")
        self.new_pwd_entry.pack(anchor="w", pady=(0, 10))

        self.confirm_pwd_entry = ctk.CTkEntry(pwd_inner, placeholder_text="Confirm New Password", show="•", width=320, fg_color=COLOR_INPUT_BG, border_color="#374151")
        self.confirm_pwd_entry.pack(anchor="w", pady=(0, 10))

        self.pwd_status_lbl = ctk.CTkLabel(pwd_inner, text="", font=("Helvetica", 11), text_color=COLOR_DANGER)
        self.pwd_status_lbl.pack(anchor="w", pady=(0, 8))

        change_btn = ctk.CTkButton(
            pwd_inner,
            text="Update Password",
            font=("Helvetica", 12, "bold"),
            fg_color=COLOR_ACCENT,
            hover_color="#7C3AED",
            width=140,
            command=self._on_update_password
        )
        change_btn.pack(anchor="w")

        # --- Card 3: Cryptographic Specifications ---
        sec_card = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=12, border_width=1, border_color="#1E293B")
        sec_card.pack(fill="x", pady=(0, 20))

        sec_inner = ctk.CTkFrame(sec_card, fg_color="transparent")
        sec_inner.pack(fill="both", expand=True, padx=25, pady=20)

        sec_title = ctk.CTkLabel(sec_inner, text="🛡️ Cryptographic Engine Details", font=("Helvetica", 16, "bold"), text_color=COLOR_TEXT_PRIMARY)
        sec_title.pack(anchor="w", pady=(0, 10))

        specs = [
            ("Symmetric Cipher:", "AES-256-GCM (Authenticated Encryption)"),
            ("Nonce Policy:", "Fresh 96-bit (12 bytes) cryptographically random nonce per message/chunk"),
            ("Key Agreement:", "Curve25519 (X25519) Ephemeral Diffie-Hellman"),
            ("Key Derivation:", "HKDF (HMAC-SHA256) with application context binding"),
            ("Password Hashing:", "Argon2id (64 MB memory cost, 3 time cost) / PBKDF2-HMAC-SHA256 fallback"),
            ("File Integrity Check:", "SHA-256 Checksum validation on assembled files"),
            ("Database Security:", "SQLite parameterized queries, never stores plaintext secrets or passwords")
        ]

        for label, val in specs:
            r = ctk.CTkFrame(sec_inner, fg_color="transparent")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=label, font=("Helvetica", 11, "bold"), text_color=COLOR_TEXT_MUTED, width=170, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=val, font=("Helvetica", 11), text_color=COLOR_TEXT_PRIMARY).pack(side="left")

        # --- Card 4: Academic Project Information ---
        info_card = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=12, border_width=1, border_color="#1E293B")
        info_card.pack(fill="x", pady=(0, 10))

        info_inner = ctk.CTkFrame(info_card, fg_color="transparent")
        info_inner.pack(fill="both", expand=True, padx=25, pady=20)

        i_title = ctk.CTkLabel(info_inner, text="🎓 Project Information", font=("Helvetica", 16, "bold"), text_color=COLOR_TEXT_PRIMARY)
        i_title.pack(anchor="w", pady=(0, 10))

        proj_details = [
            ("Application:", f"{APP_NAME} v{APP_VERSION}"),
            ("Developer / Student:", STUDENT_NAME),
            ("University ID:", STUDENT_ID),
            ("Subject Code:", SUBJECT_CODE),
            ("Project Group:", PROJECT_GROUP),
            ("Project Type:", "Syllabus Project")
        ]

        for label, val in proj_details:
            r = ctk.CTkFrame(info_inner, fg_color="transparent")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=label, font=("Helvetica", 11, "bold"), text_color=COLOR_TEXT_MUTED, width=170, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=val, font=("Helvetica", 11), text_color=COLOR_TEXT_PRIMARY).pack(side="left")

    def _on_browse_downloads(self):
        new_dir = filedialog.askdirectory(initialdir=self.current_downloads_path)
        if new_dir:
            self.current_downloads_path = new_dir
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, new_dir)
            self.network_mgr.file_transfer.downloads_dir = Path(new_dir)
            self.network_mgr.db.set_setting("downloads_dir", new_dir)

    def _on_update_password(self):
        old_pwd = self.old_pwd_entry.get()
        new_pwd = self.new_pwd_entry.get()
        confirm = self.confirm_pwd_entry.get()
        user = self.network_mgr.current_username

        if not old_pwd or not new_pwd or not confirm:
            self.pwd_status_lbl.configure(text="Please fill in all password fields.", text_color=COLOR_DANGER)
            return

        if new_pwd != confirm:
            self.pwd_status_lbl.configure(text="New passwords do not match.", text_color=COLOR_DANGER)
            return

        try:
            success = self.network_mgr.auth.change_password(user, old_pwd, new_pwd)
            if success:
                self.pwd_status_lbl.configure(text="Password successfully changed!", text_color=COLOR_SUCCESS)
                self.old_pwd_entry.delete(0, "end")
                self.new_pwd_entry.delete(0, "end")
                self.confirm_pwd_entry.delete(0, "end")
            else:
                self.pwd_status_lbl.configure(text="Failed to update password.", text_color=COLOR_DANGER)
        except Exception as e:
            self.pwd_status_lbl.configure(text=str(e), text_color=COLOR_DANGER)
