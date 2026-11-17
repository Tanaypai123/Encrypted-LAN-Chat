"""
File Sharing Interface View.
Provides UI for file selection, SHA-256 integrity preview, chunked transfer progress bars,
incoming transfer acceptance dialogs, and download folder access.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import os
import sys
import subprocess
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog
from typing import Optional, List, Dict, Any

from config import (
    COLOR_BG_DARK,
    COLOR_CARD,
    COLOR_CARD_SECONDARY,
    COLOR_INPUT_BG,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_ACCENT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_WARNING,
    DOWNLOADS_DIR
)
from gui.components import format_bytes
from app.encryption import compute_file_sha256
from app.network_manager import NetworkManager

class FileSharingView(ctk.CTkFrame):
    """Modern dark-themed File Sharing Hub."""

    def __init__(self, master, network_mgr: NetworkManager, **kwargs):
        super().__init__(master, fg_color=COLOR_BG_DARK, **kwargs)
        self.network_mgr = network_mgr

        self.selected_file_path: Optional[str] = None
        self.selected_file_hash: Optional[str] = None
        self.selected_file_size: int = 0
        self.online_users_list: List[str] = []

        # Transfer progress tracking widgets: {transfer_id: {"bar": ctk.CTkProgressBar, "pct_lbl": ctk.CTkLabel, "status_lbl": ctk.CTkLabel}}
        self._active_transfer_widgets: Dict[str, Dict[str, Any]] = {}

        self._build_ui()

    def _build_ui(self):
        # Main scrollable canvas container
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLOR_BG_DARK)
        scroll.pack(fill="both", expand=True, padx=25, pady=20)

        # Title Header
        header = ctk.CTkLabel(
            scroll,
            text="Secure File Sharing",
            font=("Helvetica", 22, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        header.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(
            scroll,
            text="Peer-to-peer chunked file transfer encrypted with AES-256-GCM and SHA-256 validation.",
            font=("Helvetica", 12),
            text_color=COLOR_TEXT_MUTED
        )
        sub.pack(anchor="w", pady=(0, 20))

        # --- Card 1: Send File Container ---
        send_card = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=12, border_width=1, border_color="#1E293B")
        send_card.pack(fill="x", pady=(0, 20))

        send_card_inner = ctk.CTkFrame(send_card, fg_color="transparent")
        send_card_inner.pack(fill="both", expand=True, padx=25, pady=20)

        card1_title = ctk.CTkLabel(
            send_card_inner,
            text="📤 Send Encrypted File",
            font=("Helvetica", 16, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        card1_title.pack(anchor="w", pady=(0, 15))

        # Row 1: Recipient Selection
        row1 = ctk.CTkFrame(send_card_inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 12))

        recip_lbl = ctk.CTkLabel(row1, text="Select Recipient:", font=("Helvetica", 12, "bold"), text_color=COLOR_TEXT_MUTED, width=120, anchor="w")
        recip_lbl.pack(side="left")

        self.recipient_dropdown = ctk.CTkOptionMenu(
            row1,
            values=["No online peers"],
            fg_color=COLOR_INPUT_BG,
            button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_PRIMARY_HOVER,
            width=220
        )
        self.recipient_dropdown.pack(side="left")

        # Row 2: File Picker
        row2 = ctk.CTkFrame(send_card_inner, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 15))

        choose_lbl = ctk.CTkLabel(row2, text="Choose File:", font=("Helvetica", 12, "bold"), text_color=COLOR_TEXT_MUTED, width=120, anchor="w")
        choose_lbl.pack(side="left")

        self.pick_btn = ctk.CTkButton(
            row2,
            text="Browse Files...",
            font=("Helvetica", 12, "bold"),
            fg_color="#374151",
            hover_color="#4B5563",
            width=130,
            command=self._on_choose_file
        )
        self.pick_btn.pack(side="left", padx=(0, 10))

        self.file_name_display = ctk.CTkLabel(
            row2,
            text="No file selected",
            font=("Helvetica", 12),
            text_color=COLOR_TEXT_MUTED
        )
        self.file_name_display.pack(side="left")

        # File Metadata Preview Box
        self.meta_box = ctk.CTkFrame(send_card_inner, fg_color=COLOR_CARD_SECONDARY, corner_radius=8)
        self.meta_box.pack(fill="x", pady=(0, 15))

        self.meta_lbl = ctk.CTkLabel(
            self.meta_box,
            text="Select a file to inspect size, chunk counts, and cryptographic hash.",
            font=("Helvetica", 11),
            text_color=COLOR_TEXT_MUTED
        )
        self.meta_lbl.pack(padx=15, pady=10)

        # Send Button
        self.send_file_btn = ctk.CTkButton(
            send_card_inner,
            text="Encrypt & Transfer File 🚀",
            font=("Helvetica", 13, "bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            height=38,
            command=self._on_send_file_click
        )
        self.send_file_btn.pack(anchor="w")
        self.send_file_btn.configure(state="disabled")

        # --- Card 2: Active & Recent Transfers ---
        trans_card = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=12, border_width=1, border_color="#1E293B")
        trans_card.pack(fill="x", pady=(0, 20))

        trans_card_inner = ctk.CTkFrame(trans_card, fg_color="transparent")
        trans_card_inner.pack(fill="both", expand=True, padx=25, pady=20)

        top_row = ctk.CTkFrame(trans_card_inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 15))

        card2_title = ctk.CTkLabel(
            top_row,
            text="📊 Active & Recent Transfers",
            font=("Helvetica", 16, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        card2_title.pack(side="left")

        open_folder_btn = ctk.CTkButton(
            top_row,
            text="📂 Open Downloads Folder",
            font=("Helvetica", 11, "bold"),
            fg_color="#1E1B4B",
            hover_color="#312E81",
            text_color="#A5B4FC",
            height=30,
            command=self._open_downloads_folder
        )
        open_folder_btn.pack(side="right")

        self.transfers_container = ctk.CTkFrame(trans_card_inner, fg_color="transparent")
        self.transfers_container.pack(fill="x")

        self.no_transfers_lbl = ctk.CTkLabel(
            self.transfers_container,
            text="No active or recent file transfers.",
            font=("Helvetica", 12),
            text_color=COLOR_TEXT_MUTED
        )
        self.no_transfers_lbl.pack(pady=20)

    def update_online_users(self, users: List[Dict[str, Any]]):
        """Update the recipient dropdown with current online users."""
        current_user = self.network_mgr.current_username
        self.online_users_list = [u["username"] for u in users if u["username"] != current_user]

        if self.online_users_list:
            self.recipient_dropdown.configure(values=self.online_users_list)
            if self.recipient_dropdown.get() not in self.online_users_list:
                self.recipient_dropdown.set(self.online_users_list[0])
            self._check_ready_to_send()
        else:
            self.recipient_dropdown.configure(values=["No online peers"])
            self.recipient_dropdown.set("No online peers")
            self.send_file_btn.configure(state="disabled")

    def preselect_recipient(self, recipient: str):
        """Preselect a recipient when arriving from chat shortcut."""
        if recipient in self.online_users_list:
            self.recipient_dropdown.set(recipient)
            self._check_ready_to_send()

    def _on_choose_file(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        path = Path(file_path)
        self.selected_file_path = str(path)
        self.selected_file_size = path.stat().st_size
        self.file_name_display.configure(text=f"{path.name} ({format_bytes(self.selected_file_size)})")

        # Compute SHA-256 for user preview
        sha256 = compute_file_sha256(self.selected_file_path)
        self.selected_file_hash = sha256

        self.meta_lbl.configure(
            text=f"Filename: {path.name}\n"
                 f"Size: {format_bytes(self.selected_file_size)} ({self.selected_file_size:,} bytes)\n"
                 f"SHA-256: {sha256[:16]}...{sha256[-16:]}",
            justify="left"
        )
        self._check_ready_to_send()

    def _check_ready_to_send(self):
        recip = self.recipient_dropdown.get()
        if recip and recip != "No online peers" and self.selected_file_path:
            self.send_file_btn.configure(state="normal")
        else:
            self.send_file_btn.configure(state="disabled")

    def _on_send_file_click(self):
        recipient = self.recipient_dropdown.get()
        if not recipient or recipient == "No online peers" or not self.selected_file_path:
            return

        transfer_id = self.network_mgr.send_file(recipient, self.selected_file_path)
        if transfer_id:
            filename = Path(self.selected_file_path).name
            self.add_transfer_row(
                transfer_id=transfer_id,
                filename=filename,
                peer=recipient,
                file_size=self.selected_file_size,
                is_outgoing=True
            )

    def add_transfer_row(self, transfer_id: str, filename: str, peer: str, file_size: int, is_outgoing: bool):
        """Add an active transfer progress card into the transfers container."""
        if self.no_transfers_lbl.winfo_exists():
            self.no_transfers_lbl.pack_forget()

        row = ctk.CTkFrame(self.transfers_container, fg_color=COLOR_CARD_SECONDARY, corner_radius=10)
        row.pack(fill="x", pady=6)

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=12)

        # Top row: icon + filename + peer
        title_row = ctk.CTkFrame(inner, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 6))

        direction = "➡️ Sending to" if is_outgoing else "⬅️ Receiving from"
        file_lbl = ctk.CTkLabel(
            title_row,
            text=f"📁 {filename}  ({format_bytes(file_size)})",
            font=("Helvetica", 13, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        file_lbl.pack(side="left")

        peer_lbl = ctk.CTkLabel(
            title_row,
            text=f"{direction} @{peer}",
            font=("Helvetica", 11),
            text_color=COLOR_ACCENT
        )
        peer_lbl.pack(side="right")

        # Progress bar
        pbar = ctk.CTkProgressBar(inner, height=8, corner_radius=4, fg_color="#374151", progress_color=COLOR_PRIMARY)
        pbar.set(0.0)
        pbar.pack(fill="x", pady=(0, 6))

        # Bottom info row: status + percentage
        bot_row = ctk.CTkFrame(inner, fg_color="transparent")
        bot_row.pack(fill="x")

        status_lbl = ctk.CTkLabel(
            bot_row,
            text="Initializing...",
            font=("Helvetica", 11),
            text_color=COLOR_TEXT_MUTED
        )
        status_lbl.pack(side="left")

        pct_lbl = ctk.CTkLabel(
            bot_row,
            text="0%",
            font=("Helvetica", 11, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        pct_lbl.pack(side="right")

        self._active_transfer_widgets[transfer_id] = {
            "row": row,
            "bar": pbar,
            "status_lbl": status_lbl,
            "pct_lbl": pct_lbl,
            "total_size": file_size
        }

    def update_progress(self, transfer_id: str, percent: float, status: str, bytes_done: int, total_bytes: int):
        """Update transfer progress bar and percentage label."""
        widgets = self._active_transfer_widgets.get(transfer_id)
        if not widgets:
            return

        pbar = widgets["bar"]
        status_lbl = widgets["status_lbl"]
        pct_lbl = widgets["pct_lbl"]

        pbar.set(percent / 100.0)
        pct_lbl.configure(text=f"{percent:.1f}%")
        status_lbl.configure(text=f"{status} ({format_bytes(bytes_done)} / {format_bytes(total_bytes)})")

        if percent >= 100.0:
            pbar.configure(progress_color=COLOR_SUCCESS)
            status_lbl.configure(text=f"Completed & Verified ({format_bytes(total_bytes)})", text_color=COLOR_SUCCESS)

    def handle_incoming_request(self, req: Dict[str, Any]):
        """Show modern modal prompt for incoming file transfer."""
        tid = req["transfer_id"]
        fname = req["filename"]
        fsize = req["file_size"]
        sender = req["sender"]
        sha256 = req["sha256"]

        # Automatically create transfer row in UI
        self.add_transfer_row(
            transfer_id=tid,
            filename=fname,
            peer=sender,
            file_size=fsize,
            is_outgoing=False
        )

        # Popup confirmation window
        popup = ctk.CTkToplevel(self)
        popup.title("Incoming Encrypted File")
        popup.geometry("450x260")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        popup.configure(fg_color=COLOR_BG_DARK)

        content = ctk.CTkFrame(popup, fg_color=COLOR_CARD, corner_radius=12)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkLabel(
            content,
            text="📥 Incoming Encrypted File",
            font=("Helvetica", 16, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        header.pack(pady=(10, 10))

        info_lbl = ctk.CTkLabel(
            content,
            text=f"User @{sender} wants to send you:\n\n"
                 f"📄 {fname}\n"
                 f"📊 Size: {format_bytes(fsize)}\n"
                 f"🔒 SHA-256: {sha256[:16]}...{sha256[-8:]}",
            font=("Helvetica", 12),
            text_color=COLOR_TEXT_PRIMARY,
            justify="center"
        )
        info_lbl.pack(pady=(0, 15))

        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack(pady=(0, 10))

        def accept():
            popup.destroy()
            self.network_mgr.accept_file(tid)

        def reject():
            popup.destroy()
            self.network_mgr.reject_file(tid)

        accept_btn = ctk.CTkButton(
            btn_row,
            text="Accept & Decrypt",
            font=("Helvetica", 12, "bold"),
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            width=130,
            command=accept
        )
        accept_btn.pack(side="left", padx=10)

        reject_btn = ctk.CTkButton(
            btn_row,
            text="Decline",
            font=("Helvetica", 12, "bold"),
            fg_color=COLOR_DANGER,
            hover_color="#DC2626",
            width=100,
            command=reject
        )
        reject_btn.pack(side="left", padx=10)

    def _open_downloads_folder(self):
        """Open the downloads folder in system file manager (macOS Finder, Windows Explorer, Linux)."""
        d_path = DOWNLOADS_DIR.resolve()
        if sys.platform == "darwin":
            subprocess.run(["open", str(d_path)])
        elif sys.platform == "win32":
            os.startfile(str(d_path))
        else:
            subprocess.run(["xdg-open", str(d_path)])
