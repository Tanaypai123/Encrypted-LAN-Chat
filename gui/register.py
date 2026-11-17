"""
Registration Screen View.
Allows new users to create accounts with client-side credential verification
and secure cryptographic transmission to the LAN server.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import threading
import customtkinter as ctk
from typing import Callable

from config import (
    DEFAULT_CLIENT_CONNECT_PORT,
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

class RegisterFrame(ctk.CTkFrame):
    """Modern dark-themed Registration View."""

    def __init__(
        self,
        master,
        network_mgr: NetworkManager,
        on_register_success: Callable[[], None],
        on_switch_to_login: Callable[[], None],
        **kwargs
    ):
        super().__init__(master, fg_color=COLOR_BG_DARK, **kwargs)
        self.network_mgr = network_mgr
        self.on_register_success = on_register_success
        self.on_switch_to_login = on_switch_to_login

        self._build_ui()

    def _build_ui(self):
        center_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=16, border_width=1, border_color="#1E293B")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        content_box = ctk.CTkFrame(center_frame, fg_color="transparent")
        content_box.pack(padx=40, pady=30)

        # Title
        title = ctk.CTkLabel(
            content_box,
            text="Create New Account",
            font=("Helvetica", 22, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            content_box,
            text="Register with the LAN Server securely",
            font=("Helvetica", 12),
            text_color=COLOR_TEXT_MUTED
        )
        subtitle.pack(pady=(2, 15))

        # Server Setting Row
        server_row = ctk.CTkFrame(content_box, fg_color="transparent")
        server_row.pack(fill="x", pady=(0, 10))

        ip_label = ctk.CTkLabel(server_row, text="Server IP:", font=("Helvetica", 11, "bold"), text_color=COLOR_TEXT_MUTED)
        ip_label.pack(side="left", padx=(0, 5))

        self.ip_entry = ctk.CTkEntry(
            server_row,
            placeholder_text="127.0.0.1",
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
        user_label = ctk.CTkLabel(content_box, text="Username (3-30 letters/numbers)", font=("Helvetica", 11, "bold"), text_color=COLOR_TEXT_PRIMARY, anchor="w")
        user_label.pack(fill="x", pady=(5, 3))

        self.username_entry = ctk.CTkEntry(
            content_box,
            placeholder_text="Choose a unique username",
            width=320,
            height=36,
            fg_color=COLOR_INPUT_BG,
            border_color="#374151"
        )
        self.username_entry.pack(pady=(0, 10))

        # Password Input
        pass_label = ctk.CTkLabel(content_box, text="Password (min 8 chars, uppercase & digit)", font=("Helvetica", 11, "bold"), text_color=COLOR_TEXT_PRIMARY, anchor="w")
        pass_label.pack(fill="x", pady=(0, 3))

        self.password_entry = ctk.CTkEntry(
            content_box,
            placeholder_text="Enter secure password",
            show="•",
            width=320,
            height=36,
            fg_color=COLOR_INPUT_BG,
            border_color="#374151"
        )
        self.password_entry.pack(pady=(0, 10))

        # Confirm Password Input
        confirm_label = ctk.CTkLabel(content_box, text="Confirm Password", font=("Helvetica", 11, "bold"), text_color=COLOR_TEXT_PRIMARY, anchor="w")
        confirm_label.pack(fill="x", pady=(0, 3))

        self.confirm_entry = ctk.CTkEntry(
            content_box,
            placeholder_text="Re-enter password",
            show="•",
            width=320,
            height=36,
            fg_color=COLOR_INPUT_BG,
            border_color="#374151"
        )
        self.confirm_entry.pack(pady=(0, 12))
        self.confirm_entry.bind("<Return>", lambda e: self._on_register_click())

        # Status / Feedback label
        self.status_label = ctk.CTkLabel(
            content_box,
            text="",
            font=("Helvetica", 11),
            text_color=COLOR_DANGER,
            wraplength=320
        )
        self.status_label.pack(pady=(0, 8))

        # Register Button
        self.register_btn = ctk.CTkButton(
            content_box,
            text="Create Account",
            font=("Helvetica", 14, "bold"),
            fg_color=COLOR_ACCENT,
            hover_color="#7C3AED",
            height=40,
            width=320,
            command=self._on_register_click
        )
        self.register_btn.pack(pady=(0, 12))

        # Back to Login Link
        login_row = ctk.CTkFrame(content_box, fg_color="transparent")
        login_row.pack()

        have_acc_label = ctk.CTkLabel(login_row, text="Already have an account?", font=("Helvetica", 12), text_color=COLOR_TEXT_MUTED)
        have_acc_label.pack(side="left", padx=(0, 5))

        login_link = ctk.CTkButton(
            login_row,
            text="Sign In",
            font=("Helvetica", 12, "bold"),
            text_color="#60A5FA",
            fg_color="transparent",
            hover_color="#1E293B",
            width=65,
            command=self.on_switch_to_login
        )
        login_link.pack(side="left")

    def _on_register_click(self):
        host = self.ip_entry.get().strip() or "127.0.0.1"
        port_str = self.port_entry.get().strip()
        username = self.username_entry.get().strip()
        pwd = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if not username or not pwd or not confirm:
            self._show_error("All fields are required.")
            return

        if pwd != confirm:
            self._show_error("Passwords do not match.")
            return

        try:
            port = int(port_str)
        except ValueError:
            self._show_error("Invalid port number.")
            return

        self.register_btn.configure(state="disabled", text="Registering...")
        self.status_label.configure(text="Contacting server...", text_color=COLOR_TEXT_MUTED)

        def worker():
            try:
                res = self.network_mgr.register(host, port, username, pwd)
                if res.get("success"):
                    self.after(0, lambda: self._on_success(res.get("message", "Registration successful!")))
                else:
                    err = res.get("error", "Registration rejected by server.")
                    self.after(0, lambda: self._show_error(err))
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))
            finally:
                self.after(0, lambda: self.register_btn.configure(state="normal", text="Create Account"))

        threading.Thread(target=worker, daemon=True).start()

    def _on_success(self, msg: str):
        self.status_label.configure(text=f"{msg} You may now sign in.", text_color=COLOR_SUCCESS)
        self.after(1500, self.on_switch_to_login)

    def _show_error(self, message: str):
        self.status_label.configure(text=message, text_color=COLOR_DANGER)
