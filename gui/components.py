"""
Reusable CustomTkinter UI Components.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable
import time

from config import (
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_BG_DARK,
    COLOR_CARD,
    COLOR_CARD_SECONDARY,
    COLOR_INPUT_BG,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER
)

def format_bytes(size_bytes: int) -> str:
    """Format bytes into human-readable string (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

class StatusBadge(ctk.CTkFrame):
    """Pill-style status badge (e.g. 'Online', 'Connected')."""

    def __init__(self, master, text: str = "Online", color: str = COLOR_SUCCESS, **kwargs):
        super().__init__(master, fg_color=COLOR_CARD_SECONDARY, corner_radius=12, border_width=1, border_color=color, **kwargs)

        self.dot = ctk.CTkLabel(
            self,
            text="●",
            text_color=color,
            font=("Helvetica", 11, "bold"),
            width=12
        )
        self.dot.pack(side="left", padx=(8, 2), pady=2)

        self.label = ctk.CTkLabel(
            self,
            text=text,
            text_color=COLOR_TEXT_PRIMARY,
            font=("Helvetica", 11, "bold")
        )
        self.label.pack(side="left", padx=(2, 8), pady=2)

    def set_status(self, text: str, color: str):
        self.configure(border_color=color)
        self.dot.configure(text_color=color)
        self.label.configure(text=text)

class EncryptionIndicator(ctk.CTkFrame):
    """Encrypted Connection indicator showing algorithm details."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="#1E1B4B",  # Deep indigo/purple background
            corner_radius=8,
            border_width=1,
            border_color="#6366F1",
            **kwargs
        )

        self.icon = ctk.CTkLabel(
            self,
            text="🔒",
            font=("Helvetica", 12)
        )
        self.icon.pack(side="left", padx=(8, 4), pady=4)

        self.text_label = ctk.CTkLabel(
            self,
            text="E2E Encrypted (AES-256-GCM / X25519)",
            text_color="#C7D2FE",
            font=("Helvetica", 11, "bold")
        )
        self.text_label.pack(side="left", padx=(0, 8), pady=4)

    def set_active(self, is_active: bool, algorithm_text: str = "AES-256-GCM / X25519"):
        if is_active:
            self.configure(fg_color="#1E1B4B", border_color="#6366F1")
            self.icon.configure(text="🔒")
            self.text_label.configure(text=f"E2E Encrypted ({algorithm_text})", text_color="#C7D2FE")
        else:
            self.configure(fg_color="#312E81", border_color="#475569")
            self.icon.configure(text="🔓")
            self.text_label.configure(text="Awaiting Handshake...", text_color="#94A3B8")

class MessageBubble(ctk.CTkFrame):
    """Chat message bubble with distinct styles for incoming and outgoing messages."""

    def __init__(
        self,
        master,
        sender: str,
        text: str,
        timestamp: str,
        is_outgoing: bool = False,
        **kwargs
    ):
        # Outgoing gets accent blue/purple; incoming gets charcoal card background
        bg_color = COLOR_PRIMARY if is_outgoing else COLOR_CARD_SECONDARY
        border_color = COLOR_PRIMARY_HOVER if is_outgoing else COLOR_BORDER

        super().__init__(
            master,
            fg_color=bg_color,
            corner_radius=14,
            border_width=1,
            border_color=border_color,
            **kwargs
        )

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(8, 2))

        sender_label = ctk.CTkLabel(
            header_frame,
            text="You" if is_outgoing else sender,
            font=("Helvetica", 11, "bold"),
            text_color="#FFFFFF" if is_outgoing else COLOR_ACCENT
        )
        sender_label.pack(side="left")

        time_str = timestamp.split(" ")[-1] if " " in timestamp else timestamp
        time_label = ctk.CTkLabel(
            header_frame,
            text=time_str,
            font=("Helvetica", 9),
            text_color="#E0E7FF" if is_outgoing else COLOR_TEXT_MUTED
        )
        time_label.pack(side="right", padx=(8, 0))

        content_label = ctk.CTkLabel(
            self,
            text=text,
            font=("Helvetica", 13),
            text_color="#FFFFFF",
            wraplength=480,
            justify="left",
            anchor="w"
        )
        content_label.pack(fill="x", padx=12, pady=(2, 8))
