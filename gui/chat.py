"""
Chat Interface View.
Displays end-to-end encrypted chat message streams, user status badges,
message composition tools, and file attachment shortcuts.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import time
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional, List, Dict, Any

from config import (
    COLOR_BG_DARK,
    COLOR_CARD,
    COLOR_CARD_SECONDARY,
    COLOR_INPUT_BG,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_ACCENT
)
from gui.components import MessageBubble, EncryptionIndicator
from app.network_manager import NetworkManager

class ChatView(ctk.CTkFrame):
    """Encrypted Chat Interface for communicating with a selected peer."""

    def __init__(
        self,
        master,
        network_mgr: NetworkManager,
        on_send_file_shortcut: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=COLOR_BG_DARK, **kwargs)
        self.network_mgr = network_mgr
        self.on_send_file_shortcut = on_send_file_shortcut
        self.current_peer: Optional[str] = None

        self._build_ui()

    def _build_ui(self):
        # 1. Chat Header Bar
        self.header = ctk.CTkFrame(self, fg_color=COLOR_CARD, height=60, corner_radius=0)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        header_content = ctk.CTkFrame(self.header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=10)

        # Peer Avatar Icon + Name
        left_info = ctk.CTkFrame(header_content, fg_color="transparent")
        left_info.pack(side="left")

        self.peer_avatar = ctk.CTkLabel(
            left_info,
            text="👤",
            font=("Helvetica", 18),
            width=30
        )
        self.peer_avatar.pack(side="left", padx=(0, 8))

        self.peer_label = ctk.CTkLabel(
            left_info,
            text="Select a contact to begin messaging",
            font=("Helvetica", 15, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        self.peer_label.pack(side="left")

        # Encryption Indicator on Header Right
        right_actions = ctk.CTkFrame(header_content, fg_color="transparent")
        right_actions.pack(side="right")

        self.enc_badge = EncryptionIndicator(right_actions)
        self.enc_badge.pack(side="left", padx=(0, 15))

        self.attach_btn = ctk.CTkButton(
            right_actions,
            text="📎 Send File",
            font=("Helvetica", 12, "bold"),
            fg_color="#374151",
            hover_color="#4B5563",
            width=100,
            height=32,
            command=self._on_attach_click
        )
        self.attach_btn.pack(side="left")
        self.attach_btn.configure(state="disabled")

        # 2. Scrollable Messages Area
        self.messages_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLOR_BG_DARK,
            corner_radius=0
        )
        self.messages_scroll.pack(fill="both", expand=True, padx=15, pady=10)

        # Welcome Placeholder
        self.placeholder_label = ctk.CTkLabel(
            self.messages_scroll,
            text="Select an online user from the right sidebar to start an end-to-end encrypted conversation.",
            font=("Helvetica", 13),
            text_color=COLOR_TEXT_MUTED
        )
        self.placeholder_label.pack(pady=100)

        # 3. Bottom Input Bar
        self.input_bar = ctk.CTkFrame(self, fg_color=COLOR_CARD, height=65, corner_radius=0)
        self.input_bar.pack(fill="x", side="bottom")
        self.input_bar.pack_propagate(False)

        input_container = ctk.CTkFrame(self.input_bar, fg_color="transparent")
        input_container.pack(fill="both", expand=True, padx=20, pady=12)

        self.msg_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="Select a peer first...",
            font=("Helvetica", 13),
            fg_color=COLOR_INPUT_BG,
            border_color="#374151",
            height=40
        )
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.msg_entry.bind("<Return>", lambda e: self._on_send_click())
        self.msg_entry.configure(state="disabled")

        self.send_btn = ctk.CTkButton(
            input_container,
            text="Send 📤",
            font=("Helvetica", 13, "bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            width=90,
            height=40,
            command=self._on_send_click
        )
        self.send_btn.pack(side="right")
        self.send_btn.configure(state="disabled")

    def set_active_peer(self, peer_username: str):
        """Switch active conversation to the specified peer."""
        if self.current_peer == peer_username:
            return

        self.current_peer = peer_username
        self.peer_label.configure(text=f"@{peer_username}")
        self.msg_entry.configure(
            state="normal",
            placeholder_text=f"Type a secure message to @{peer_username}..."
        )
        self.send_btn.configure(state="normal")
        self.attach_btn.configure(state="normal")

        # Update encryption badge
        has_key = self.network_mgr.has_encryption_key_for(peer_username)
        self.enc_badge.set_active(has_key)

        # Clear scroll area and reload message history from SQLite
        self._clear_messages_view()
        self._load_conversation_history()

    def _clear_messages_view(self):
        for widget in self.messages_scroll.winfo_children():
            widget.destroy()

    def _load_conversation_history(self):
        """Fetch past messages between current user and peer from database."""
        if not self.current_peer:
            return

        history = self.network_mgr.get_chat_history(self.current_peer)
        current_user = self.network_mgr.current_username

        if not history:
            info_card = ctk.CTkFrame(self.messages_scroll, fg_color=COLOR_CARD_SECONDARY, corner_radius=10)
            info_card.pack(pady=20, padx=40, fill="x")

            info_lbl = ctk.CTkLabel(
                info_card,
                text=f"This is the beginning of your end-to-end encrypted chat with @{self.current_peer}.\n"
                     f"Messages are protected by AES-256-GCM and Curve25519 key exchange.",
                font=("Helvetica", 11),
                text_color=COLOR_TEXT_MUTED,
                justify="center"
            )
            info_lbl.pack(padx=20, pady=15)
            return

        for msg in history:
            is_out = (msg["sender_username"] == current_user)
            self._render_bubble(
                sender=msg["sender_username"],
                text=msg["message_content"],
                timestamp=msg.get("timestamp", ""),
                is_outgoing=is_out
            )

        self._scroll_to_bottom()

    def _render_bubble(self, sender: str, text: str, timestamp: str, is_outgoing: bool):
        row_frame = ctk.CTkFrame(self.messages_scroll, fg_color="transparent")
        row_frame.pack(fill="x", pady=4, padx=10)

        bubble = MessageBubble(
            row_frame,
            sender=sender,
            text=text,
            timestamp=timestamp,
            is_outgoing=is_outgoing
        )
        # Right align for outgoing, Left align for incoming
        if is_outgoing:
            bubble.pack(side="right", anchor="e")
        else:
            bubble.pack(side="left", anchor="w")

    def append_incoming_message(self, sender: str, text: str, timestamp: str):
        """Append real-time incoming message if it belongs to active conversation."""
        if sender == self.current_peer:
            self._render_bubble(sender, text, timestamp, is_outgoing=False)
            self.enc_badge.set_active(True)
            self._scroll_to_bottom()

    def _on_send_click(self):
        if not self.current_peer:
            return

        text = self.msg_entry.get().strip()
        if not text:
            return

        self.msg_entry.delete(0, "end")
        ts = time.strftime("%Y-%m-%d %H:%M:%S")

        # Render outgoing bubble immediately
        self._render_bubble("You", text, ts, is_outgoing=True)
        self._scroll_to_bottom()

        # Send encrypted message via network manager
        success = self.network_mgr.send_chat(self.current_peer, text)
        if success:
            self.enc_badge.set_active(True)

    def _on_attach_click(self):
        """Open file picker to send a file to the active peer."""
        if not self.current_peer:
            return
        if self.on_send_file_shortcut:
            self.on_send_file_shortcut(self.current_peer)

    def _scroll_to_bottom(self):
        self.after(50, lambda: self.messages_scroll._parent_canvas.yview_moveto(1.0))
