"""
Transfer & Communication History Interface View.
Displays searchable logs of completed and past file transfers and chat archives.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import customtkinter as ctk
from typing import List, Dict, Any

from config import (
    COLOR_BG_DARK,
    COLOR_CARD,
    COLOR_CARD_SECONDARY,
    COLOR_INPUT_BG,
    COLOR_PRIMARY,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_ACCENT
)
from gui.components import format_bytes
from app.network_manager import NetworkManager

class HistoryView(ctk.CTkFrame):
    """Activity History & Archive View."""

    def __init__(self, master, network_mgr: NetworkManager, **kwargs):
        super().__init__(master, fg_color=COLOR_BG_DARK, **kwargs)
        self.network_mgr = network_mgr

        self._build_ui()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLOR_BG_DARK)
        scroll.pack(fill="both", expand=True, padx=25, pady=20)

        # Header
        top_row = ctk.CTkFrame(scroll, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 15))

        header = ctk.CTkLabel(
            top_row,
            text="Transfer & Chat History",
            font=("Helvetica", 22, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        header.pack(side="left")

        refresh_btn = ctk.CTkButton(
            top_row,
            text="🔄 Refresh Records",
            font=("Helvetica", 11, "bold"),
            fg_color="#374151",
            hover_color="#4B5563",
            width=130,
            command=self.refresh_records
        )
        refresh_btn.pack(side="right")

        # Container for History Records
        self.records_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.records_container.pack(fill="both", expand=True)

        self.refresh_records()

    def refresh_records(self):
        """Fetch records from database and render cards."""
        for widget in self.records_container.winfo_children():
            widget.destroy()

        transfers = self.network_mgr.get_transfer_history()
        current_user = self.network_mgr.current_username

        if not transfers:
            empty_card = ctk.CTkFrame(self.records_container, fg_color=COLOR_CARD, corner_radius=12)
            empty_card.pack(fill="x", pady=20)

            ctk.CTkLabel(
                empty_card,
                text="No file transfers recorded in the database.",
                font=("Helvetica", 13),
                text_color=COLOR_TEXT_MUTED
            ).pack(pady=30)
            return

        for t in transfers:
            row = ctk.CTkFrame(self.records_container, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color="#1E293B")
            row.pack(fill="x", pady=6)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=20, pady=12)

            is_out = (t["sender_username"] == current_user)
            direction_str = "Outgoing ↗" if is_out else "Incoming ↙"
            peer = t["receiver_username"] if is_out else t["sender_username"]

            # Top Line
            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x", pady=(0, 4))

            fname_lbl = ctk.CTkLabel(top, text=f"📄 {t['filename']}", font=("Helvetica", 13, "bold"), text_color=COLOR_TEXT_PRIMARY)
            fname_lbl.pack(side="left")

            status = t.get("status", "unknown").capitalize()
            status_color = COLOR_SUCCESS if status == "Completed" else (COLOR_DANGER if status == "Failed" else COLOR_ACCENT)
            status_lbl = ctk.CTkLabel(top, text=f"● {status}", font=("Helvetica", 11, "bold"), text_color=status_color)
            status_lbl.pack(side="right")

            # Bottom Line: Metadata
            bot = ctk.CTkFrame(inner, fg_color="transparent")
            bot.pack(fill="x")

            fsize_str = format_bytes(t["file_size"])
            date_str = t.get("created_at", "")
            sha256_short = f"{t['sha256_hash'][:8]}...{t['sha256_hash'][-8:]}" if t.get("sha256_hash") else "N/A"

            meta_text = f"{direction_str} @{peer}  •  {fsize_str}  •  Date: {date_str}  •  SHA-256: {sha256_short}"
            meta_lbl = ctk.CTkLabel(bot, text=meta_text, font=("Helvetica", 11), text_color=COLOR_TEXT_MUTED)
            meta_lbl.pack(side="left")
