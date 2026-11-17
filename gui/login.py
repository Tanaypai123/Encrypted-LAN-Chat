"""
Login Screen View.
Provides modern authentication interface with host/port selection and local server launcher.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import threading
import customtkinter as ctk
from typing import Callable, Optional

from config import (
    DEFAULT_CLIENT_CONNECT_PORT,
    get_local_ip,
    COLOR_BG_DARK,
    COLOR_CARD,
    COLOR_INPUT_BG,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_ACCENT
)
from app.network_manager import NetworkManager

class LoginFrame(ctk.CTkFrame):
    """Modern dark-themed Login View."""

    def __init__(
        self,
        master,
        network_mgr: NetworkManager,
        on_login_success: Callable[[str], None],
        on_switch_to_register: Callable[[], None],
        on_open_server_modal: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=COLOR_BG_DARK, **kwargs)
        self.network_mgr = network_mgr
        self.on_login_success = on_login_success
        self.on_switch_to_register = on_switch_to_register
        self.on_open_server_modal = on_open_server_modal

        self._build_ui()

    def _build_ui(self):
        # Outer Centering Container
        center_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=16, border_width=1, border_color="#1E293B")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Inner Content Box
        content_box = ctk.CTkFrame(center_frame, fg_color="transparent")
        content_box.pack(padx=40, pady=35)

        # Header Badge & Title
        badge = ctk.CTkLabel(
            content_box,
            text="🔒 AES-256-GCM + X25519",
            font=("Helvetica", 11, "bold"),
            text_color="#818CF8",
            fg_color="#1E1B4B",
            corner_radius=8,
            padx=10,
            pady=4
        )
        badge.pack(pady=(0, 10))

        title = ctk.CTkLabel(
            content_box,
            text="LAN Encrypted Chat",
            font=("Helvetica", 24, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            content_box,
            text="Secure Peer-to-Peer Messaging & File Sharing",
            font=("Helvetica", 12),
            text_color=COLOR_TEXT_MUTED
        )
        subtitle.pack(pady=(2, 20))

        # Server Settings Row (IP + Port)
        server_row = ctk.CTkFrame(content_box, fg_color="transparent")
        server_row.pack(fill="x", pady=(0, 12))

        ip_label = ctk.CTkLabel(server_row, text="Server IP:", font=("Helvetica", 11, "bold"), text_color=COLOR_TEXT_MUTED)
        ip_label.pack(side="left", padx=(0, 5))

        self.ip_entry = ctk.CTkEntry(
            server_row,
            placeholder_text="127.0.0.1 or LAN IP",
            width=150,
            fg_color=COLOR_INPUT_BG,
            border_color="#374151"
        )
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(side="left", padx=(0, 10))

        port_label = ctk.CTkLabel(server_row, text="Port:", font=("Helvetica", 11, "bold"), text_color=COLOR_TEXT_MUTED)
        port_label.pack(side="left", padx=(0, 5))

        self.port_entry = ctk.CTkEntry(
            server_row,
            placeholder_text="55555",
            width=80,
            fg_color=COLOR_INPUT_BG,
            border_color="#374151"
        )
        self.port_entry.insert(0, str(DEFAULT_CLIENT_CONNECT_PORT))
        self.port_entry.pack(side="left")

        # Username Input
        user_label = ctk.CTkLabel(content_box, text="Username", font=("Helvetica", 12, "bold"), text_color=COLOR_TEXT_PRIMARY, anchor="w")
        user_label.pack(fill="x", pady=(5, 3))

        self.username_entry = ctk.CTkEntry(
            content_box,
            placeholder_text="Enter your username",
            width=320,
            height=38,
            fg_color=COLOR_INPUT_BG,
            border_color="#374151"
        )
        self.username_entry.pack(pady=(0, 12))

        # Password Input
        pass_label = ctk.CTkLabel(content_box, text="Password", font=("Helvetica", 12, "bold"), text_color=COLOR_TEXT_PRIMARY, anchor="w")
        pass_label.pack(fill="x", pady=(0, 3))

        self.password_entry = ctk.CTkEntry(
            content_box,
            placeholder_text="Enter your password",
            show="•",
            width=320,
            height=38,
            fg_color=COLOR_INPUT_BG,
            border_color="#374151"
        )
        self.password_entry.pack(pady=(0, 15))
        self.password_entry.bind("<Return>", lambda e: self._on_login_click())

        # Status / Error Feedback Message
        self.status_label = ctk.CTkLabel(
            content_box,
            text="",
            font=("Helvetica", 11),
            text_color=COLOR_DANGER,
            wraplength=320
        )
        self.status_label.pack(pady=(0, 10))

        # Login Button
        self.login_btn = ctk.CTkButton(
            content_box,
            text="Sign In",
            font=("Helvetica", 14, "bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            height=42,
            width=320,
            command=self._on_login_click
        )
        self.login_btn.pack(pady=(0, 15))

        # Switch to Register Button
        register_row = ctk.CTkFrame(content_box, fg_color="transparent")
        register_row.pack()

        no_acc_label = ctk.CTkLabel(register_row, text="Don't have an account?", font=("Helvetica", 12), text_color=COLOR_TEXT_MUTED)
        no_acc_label.pack(side="left", padx=(0, 5))

        reg_link = ctk.CTkButton(
            register_row,
            text="Register Now",
            font=("Helvetica", 12, "bold"),
            text_color="#60A5FA",
            fg_color="transparent",
            hover_color="#1E293B",
            width=90,
            command=self.on_switch_to_register
        )
        reg_link.pack(side="left")

        # Quick Host Server helper button
        if self.on_open_server_modal:
            host_btn = ctk.CTkButton(
                content_box,
                text="🖥️ Host Local Server on this Machine",
                font=("Helvetica", 11),
                text_color=COLOR_TEXT_MUTED,
                fg_color="transparent",
                hover_color="#1E293B",
                command=self.on_open_server_modal
            )
            host_btn.pack(pady=(15, 0))

    def _on_login_click(self):
        """Trigger login process in background thread to avoid freezing GUI."""
        host = self.ip_entry.get().strip() or "127.0.0.1"
        port_str = self.port_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self._show_error("Please enter both username and password.")
            return

        try:
            port = int(port_str)
        except ValueError:
            self._show_error("Port must be a valid integer.")
            return

        self.login_btn.configure(state="disabled", text="Connecting...")
        self.status_label.configure(text="Authenticating...", text_color=COLOR_TEXT_MUTED)

        def worker():
            try:
                self.network_mgr.login(host, port, username, password)
                self.after(0, lambda: self.on_login_success(username))
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda: self._on_login_failed(err_msg))

        threading.Thread(target=worker, daemon=True).start()

    def _on_login_failed(self, error: str):
        self.login_btn.configure(state="normal", text="Sign In")
        self._show_error(error)

    def _show_error(self, message: str):
        self.status_label.configure(text=message, text_color=COLOR_DANGER)
