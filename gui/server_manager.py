"""
Server Management Interface View.
Allows users to host, configure, monitor, and manage a local LAN TCP server directly from the GUI.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import customtkinter as ctk
import tkinter as tk
from typing import List, Dict, Any

from config import (
    DEFAULT_PORT,
    get_local_ip,
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
    COLOR_WARNING,
    COLOR_ACCENT
)
from gui.components import StatusBadge
from app.network_manager import NetworkManager

class ServerManagerView(ctk.CTkFrame):
    """Server Management Hub for LAN hosting."""

    def __init__(self, master, network_mgr: NetworkManager, **kwargs):
        super().__init__(master, fg_color=COLOR_BG_DARK, **kwargs)
        self.network_mgr = network_mgr

        self._build_ui()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLOR_BG_DARK)
        scroll.pack(fill="both", expand=True, padx=25, pady=20)

        # Title Header
        header = ctk.CTkLabel(
            scroll,
            text="LAN Server Control Center",
            font=("Helvetica", 22, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        header.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(
            scroll,
            text="Host a local TCP relay server for other users connected to your Wi-Fi or Ethernet network.",
            font=("Helvetica", 12),
            text_color=COLOR_TEXT_MUTED
        )
        sub.pack(anchor="w", pady=(0, 20))

        # --- Card 1: Server Control & Status ---
        ctrl_card = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=12, border_width=1, border_color="#1E293B")
        ctrl_card.pack(fill="x", pady=(0, 20))

        ctrl_inner = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        ctrl_inner.pack(fill="both", expand=True, padx=25, pady=20)

        # Status & Toggle Row
        status_row = ctk.CTkFrame(ctrl_inner, fg_color="transparent")
        status_row.pack(fill="x", pady=(0, 15))

        self.status_badge = StatusBadge(
            status_row,
            text="Server Stopped",
            color=COLOR_DANGER
        )
        self.status_badge.pack(side="left")

        # LAN IP Label with Copy
        lan_ip = get_local_ip()
        ip_row = ctk.CTkFrame(status_row, fg_color="transparent")
        ip_row.pack(side="right")

        self.ip_display = ctk.CTkLabel(
            ip_row,
            text=f"Your LAN IP: {lan_ip}",
            font=("Helvetica", 12, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        self.ip_display.pack(side="left", padx=(0, 10))

        copy_btn = ctk.CTkButton(
            ip_row,
            text="📋 Copy IP",
            font=("Helvetica", 11),
            fg_color="#374151",
            hover_color="#4B5563",
            width=80,
            height=28,
            command=lambda: self._copy_ip(lan_ip)
        )
        copy_btn.pack(side="left")

        # Port Configuration & Action Buttons
        config_row = ctk.CTkFrame(ctrl_inner, fg_color="transparent")
        config_row.pack(fill="x", pady=(0, 10))

        port_lbl = ctk.CTkLabel(config_row, text="Listening Port:", font=("Helvetica", 12, "bold"), text_color=COLOR_TEXT_MUTED)
        port_lbl.pack(side="left", padx=(0, 8))

        self.port_entry = ctk.CTkEntry(
            config_row,
            placeholder_text="55555",
            width=100,
            fg_color=COLOR_INPUT_BG,
            border_color="#374151"
        )
        self.port_entry.insert(0, str(DEFAULT_PORT))
        self.port_entry.pack(side="left", padx=(0, 15))

        self.toggle_btn = ctk.CTkButton(
            config_row,
            text="Start Server 🚀",
            font=("Helvetica", 13, "bold"),
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            height=36,
            command=self._on_toggle_server
        )
        self.toggle_btn.pack(side="left")

        # --- Card 2: Connected Clients Table ---
        clients_card = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=12, border_width=1, border_color="#1E293B")
        clients_card.pack(fill="x", pady=(0, 20))

        clients_inner = ctk.CTkFrame(clients_card, fg_color="transparent")
        clients_inner.pack(fill="both", expand=True, padx=25, pady=20)

        c_title = ctk.CTkLabel(
            clients_inner,
            text="👥 Connected Clients",
            font=("Helvetica", 16, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        c_title.pack(anchor="w", pady=(0, 12))

        self.clients_container = ctk.CTkFrame(clients_inner, fg_color="transparent")
        self.clients_container.pack(fill="x")

        self.no_clients_lbl = ctk.CTkLabel(
            self.clients_container,
            text="No clients currently connected.",
            font=("Helvetica", 12),
            text_color=COLOR_TEXT_MUTED
        )
        self.no_clients_lbl.pack(pady=15)

        # --- Card 3: Server Activity Logs Console ---
        logs_card = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=12, border_width=1, border_color="#1E293B")
        logs_card.pack(fill="both", expand=True, pady=(0, 10))

        logs_inner = ctk.CTkFrame(logs_card, fg_color="transparent")
        logs_inner.pack(fill="both", expand=True, padx=25, pady=20)

        log_head = ctk.CTkFrame(logs_inner, fg_color="transparent")
        log_head.pack(fill="x", pady=(0, 10))

        l_title = ctk.CTkLabel(
            log_head,
            text="📜 Live Server Logs",
            font=("Helvetica", 16, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        l_title.pack(side="left")

        clear_btn = ctk.CTkButton(
            log_head,
            text="Clear Logs",
            font=("Helvetica", 11),
            fg_color="#374151",
            hover_color="#4B5563",
            width=80,
            height=26,
            command=self._clear_logs
        )
        clear_btn.pack(side="right")

        self.log_textbox = ctk.CTkTextbox(
            logs_inner,
            font=("Courier", 11),
            fg_color="#0F172A",
            text_color="#94A3B8",
            height=180,
            corner_radius=8
        )
        self.log_textbox.pack(fill="both", expand=True)
        self.log_textbox.configure(state="disabled")

        # Synchronize UI if server was already started
        if self.network_mgr.is_server_running():
            self.update_server_status(True, f"{get_local_ip()}:{self.network_mgr.server.port if self.network_mgr.server else DEFAULT_PORT}")

    def _copy_ip(self, ip_str: str):
        self.clipboard_clear()
        self.clipboard_append(ip_str)

    def _on_toggle_server(self):
        if self.network_mgr.is_server_running():
            self.network_mgr.stop_server()
            self.update_server_status(False, "Stopped")
        else:
            try:
                port = int(self.port_entry.get().strip())
            except ValueError:
                port = DEFAULT_PORT

            started = self.network_mgr.start_server(port)
            if started:
                self.update_server_status(True, f"{get_local_ip()}:{port}")
            else:
                self.append_log("[Error] Failed to bind to requested port.")

    def update_server_status(self, is_running: bool, address_str: str):
        """Update GUI indicators for server status."""
        if is_running:
            self.status_badge.set_status("Server Running", COLOR_SUCCESS)
            self.toggle_btn.configure(text="Stop Server 🛑", fg_color=COLOR_DANGER, hover_color="#DC2626")
            self.port_entry.configure(state="disabled")
        else:
            self.status_badge.set_status("Server Stopped", COLOR_DANGER)
            self.toggle_btn.configure(text="Start Server 🚀", fg_color=COLOR_SUCCESS, hover_color="#059669")
            self.port_entry.configure(state="normal")

    def update_connected_clients(self, clients: List[Dict[str, Any]]):
        """Render connected clients list."""
        for widget in self.clients_container.winfo_children():
            widget.destroy()

        if not clients:
            lbl = ctk.CTkLabel(
                self.clients_container,
                text="No clients currently connected.",
                font=("Helvetica", 12),
                text_color=COLOR_TEXT_MUTED
            )
            lbl.pack(pady=15)
            return

        for c in clients:
            row = ctk.CTkFrame(self.clients_container, fg_color=COLOR_CARD_SECONDARY, corner_radius=8)
            row.pack(fill="x", pady=4)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=8)

            u_lbl = ctk.CTkLabel(inner, text=f"👤 @{c['username']}", font=("Helvetica", 12, "bold"), text_color=COLOR_TEXT_PRIMARY)
            u_lbl.pack(side="left")

            ip_lbl = ctk.CTkLabel(inner, text=f"{c['ip']}:{c['port']}", font=("Helvetica", 11), text_color=COLOR_TEXT_MUTED)
            ip_lbl.pack(side="left", padx=20)

            badge = ctk.CTkLabel(inner, text="🟢 Connected", font=("Helvetica", 10, "bold"), text_color=COLOR_SUCCESS)
            badge.pack(side="right")

    def append_log(self, log_line: str):
        """Append log message to the console."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", log_line + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def _clear_logs(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
