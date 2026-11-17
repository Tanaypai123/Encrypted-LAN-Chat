"""
Main Dashboard View.
Orchestrates Left Navigation, Center Content switching, Right Online Users sidebar,
and Bottom Status Bar with real-time reactive event hooks.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict, List, Any

from config import (
    APP_NAME,
    APP_VERSION,
    STUDENT_NAME,
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
    COLOR_DANGER,
    COLOR_WARNING,
    COLOR_ACCENT
)
from gui.components import StatusBadge, EncryptionIndicator
from gui.chat import ChatView
from gui.file_sharing import FileSharingView
from gui.server_manager import ServerManagerView
from gui.settings import SettingsView
from gui.history import HistoryView
from app.network_manager import NetworkManager

class DashboardFrame(ctk.CTkFrame):
    """The central application workspace dashboard."""

    def __init__(
        self,
        master,
        network_mgr: NetworkManager,
        on_logout: Callable[[], None],
        **kwargs
    ):
        super().__init__(master, fg_color=COLOR_BG_DARK, **kwargs)
        self.network_mgr = network_mgr
        self.on_logout = on_logout

        self.current_view_name = "chat"
        self._online_users: List[Dict[str, Any]] = []

        self._build_ui()
        self._setup_event_hooks()

    def _build_ui(self):
        # 1. Main Horizontal Split (Left Sidebar | Central Area | Right Sidebar)
        self.body_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_DARK, corner_radius=0)
        self.body_frame.pack(fill="both", expand=True, side="top")

        # 2. Bottom Status Bar (Always Visible)
        self.status_bar = ctk.CTkFrame(self, fg_color=COLOR_CARD, height=36, corner_radius=0, border_width=1, border_color="#1E293B")
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)

        self._build_bottom_status_bar()
        self._build_left_sidebar()
        self._build_center_views()
        self._build_right_sidebar()

    def _build_bottom_status_bar(self):
        inner = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15)

        # Left: Connection status
        left_box = ctk.CTkFrame(inner, fg_color="transparent")
        left_box.pack(side="left")

        self.conn_dot = ctk.CTkLabel(left_box, text="●", text_color=COLOR_SUCCESS, font=("Helvetica", 14, "bold"))
        self.conn_dot.pack(side="left", padx=(0, 4))

        self.conn_text = ctk.CTkLabel(left_box, text="Connected to LAN Server", font=("Helvetica", 11), text_color=COLOR_TEXT_PRIMARY)
        self.conn_text.pack(side="left")

        # Center: Current active user
        center_box = ctk.CTkFrame(inner, fg_color="transparent")
        center_box.place(relx=0.5, rely=0.5, anchor="center")

        current_u = self.network_mgr.current_username or "Guest"
        self.user_session_lbl = ctk.CTkLabel(
            center_box,
            text=f"👤 Logged in as: @{current_u}",
            font=("Helvetica", 11, "bold"),
            text_color="#818CF8"
        )
        self.user_session_lbl.pack()

        # Right: Security & Encryption Badge
        right_box = ctk.CTkFrame(inner, fg_color="transparent")
        right_box.pack(side="right")

        self.status_enc_badge = ctk.CTkLabel(
            right_box,
            text="🔒 AES-256-GCM / X25519 Active",
            font=("Helvetica", 10, "bold"),
            text_color="#A5B4FC"
        )
        self.status_enc_badge.pack(side="right")

    def _build_left_sidebar(self):
        self.left_nav = ctk.CTkFrame(self.body_frame, fg_color=COLOR_CARD, width=220, corner_radius=0)
        self.left_nav.pack(side="left", fill="y")
        self.left_nav.pack_propagate(False)

        # Brand / App Title
        brand_box = ctk.CTkFrame(self.left_nav, fg_color="transparent")
        brand_box.pack(fill="x", padx=15, pady=(20, 25))

        brand_title = ctk.CTkLabel(
            brand_box,
            text="LAN Encrypted",
            font=("Helvetica", 16, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        brand_title.pack(anchor="w")

        brand_sub = ctk.CTkLabel(
            brand_box,
            text="Chat & File Hub",
            font=("Helvetica", 12),
            text_color=COLOR_TEXT_MUTED
        )
        brand_sub.pack(anchor="w")

        # Nav Buttons Container
        self.nav_btns_frame = ctk.CTkFrame(self.left_nav, fg_color="transparent")
        self.nav_btns_frame.pack(fill="x", padx=10, pady=5)

        self.nav_buttons: Dict[str, ctk.CTkButton] = {}

        nav_items = [
            ("chat", "💬 Encrypted Chat"),
            ("files", "📁 File Transfer"),
            ("server", "🖥️ LAN Server"),
            ("history", "📜 Transfer History"),
            ("settings", "⚙️ Settings")
        ]

        for key, label in nav_items:
            btn = ctk.CTkButton(
                self.nav_btns_frame,
                text=label,
                font=("Helvetica", 13),
                anchor="w",
                height=40,
                corner_radius=8,
                fg_color=COLOR_PRIMARY if key == "chat" else "transparent",
                hover_color="#1E293B",
                text_color=COLOR_TEXT_PRIMARY,
                command=lambda k=key: self.switch_view(k)
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[key] = btn

        # Bottom Logout Button in Left Sidebar
        logout_btn = ctk.CTkButton(
            self.left_nav,
            text="🚪 Sign Out",
            font=("Helvetica", 12, "bold"),
            fg_color="#1E1B4B",
            hover_color="#312E81",
            text_color="#F87171",
            height=38,
            corner_radius=8,
            command=self._on_logout_click
        )
        logout_btn.pack(side="bottom", fill="x", padx=15, pady=20)

    def _build_center_views(self):
        """Build view container with stacked frames for instant view switching."""
        self.center_area = ctk.CTkFrame(self.body_frame, fg_color=COLOR_BG_DARK, corner_radius=0)
        self.center_area.pack(side="left", fill="both", expand=True)

        self.views: Dict[str, ctk.CTkFrame] = {}

        # 1. Chat View
        self.chat_view = ChatView(
            self.center_area,
            network_mgr=self.network_mgr,
            on_send_file_shortcut=self._shortcut_send_file
        )
        self.views["chat"] = self.chat_view
        self.chat_view.pack(fill="both", expand=True)

        # 2. File Sharing View
        self.file_view = FileSharingView(
            self.center_area,
            network_mgr=self.network_mgr
        )
        self.views["files"] = self.file_view

        # 3. Server Manager View
        self.server_view = ServerManagerView(
            self.center_area,
            network_mgr=self.network_mgr
        )
        self.views["server"] = self.server_view

        # 4. History View
        self.history_view = HistoryView(
            self.center_area,
            network_mgr=self.network_mgr
        )
        self.views["history"] = self.history_view

        # 5. Settings View
        self.settings_view = SettingsView(
            self.center_area,
            network_mgr=self.network_mgr
        )
        self.views["settings"] = self.settings_view

    def _build_right_sidebar(self):
        """Right Sidebar displaying Online LAN Users with presence indicators."""
        self.right_sidebar = ctk.CTkFrame(self.body_frame, fg_color=COLOR_CARD, width=240, corner_radius=0)
        self.right_sidebar.pack(side="right", fill="y")
        self.right_sidebar.pack_propagate(False)

        top_row = ctk.CTkFrame(self.right_sidebar, fg_color="transparent")
        top_row.pack(fill="x", padx=15, pady=(20, 10))

        title = ctk.CTkLabel(
            top_row,
            text="Online Users",
            font=("Helvetica", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        title.pack(side="left")

        self.user_count_badge = ctk.CTkLabel(
            top_row,
            text="0",
            font=("Helvetica", 11, "bold"),
            fg_color="#374151",
            corner_radius=10,
            width=26,
            height=20
        )
        self.user_count_badge.pack(side="right")

        sub = ctk.CTkLabel(
            self.right_sidebar,
            text="Click a user to open chat",
            font=("Helvetica", 10),
            text_color=COLOR_TEXT_MUTED
        )
        sub.pack(anchor="w", padx=15, pady=(0, 10))

        # Scrollable user list
        self.users_scroll = ctk.CTkScrollableFrame(self.right_sidebar, fg_color=COLOR_CARD, corner_radius=0)
        self.users_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.no_users_lbl = ctk.CTkLabel(
            self.users_scroll,
            text="Waiting for other users\nto join the LAN...",
            font=("Helvetica", 11),
            text_color=COLOR_TEXT_MUTED,
            justify="center"
        )
        self.no_users_lbl.pack(pady=40)

    def switch_view(self, view_name: str):
        """Switch active center frame and update navigation button styling."""
        if view_name not in self.views:
            return

        for name, frame in self.views.items():
            frame.pack_forget()

        self.views[view_name].pack(fill="both", expand=True)
        self.current_view_name = view_name

        # Update button highlighting
        for k, btn in self.nav_buttons.items():
            if k == view_name:
                btn.configure(fg_color=COLOR_PRIMARY)
            else:
                btn.configure(fg_color="transparent")

        # Specific view refresh triggers
        if view_name == "history":
            self.history_view.refresh_records()

    def _setup_event_hooks(self):
        """Wire up NetworkManager events to thread-safe GUI updates."""
        self.network_mgr.on_user_list_changed = lambda users: self.after(0, lambda: self._on_user_list_update(users))
        self.network_mgr.on_chat_received = lambda sender, text, ts, mid: self.after(0, lambda: self._on_incoming_chat(sender, text, ts))
        self.network_mgr.on_file_requested = lambda req: self.after(0, lambda: self.file_view.handle_incoming_request(req))
        self.network_mgr.on_file_progress = lambda tid, pct, st, done, tot: self.after(0, lambda: self.file_view.update_progress(tid, pct, st, done, tot))
        self.network_mgr.on_server_status_changed = lambda running, addr: self.after(0, lambda: self.server_view.update_server_status(running, addr))
        self.network_mgr.on_server_clients_changed = lambda clients: self.after(0, lambda: self.server_view.update_connected_clients(clients))
        self.network_mgr.on_log = lambda log: self.after(0, lambda: self.server_view.append_log(log))
        self.network_mgr.on_connection_changed = lambda st, r: self.after(0, lambda: self._on_conn_changed(st, r))
        self.network_mgr.on_security_alert = lambda lvl, msg: self.after(0, lambda: self._on_security_alert(lvl, msg))

    def _on_user_list_update(self, users: List[Dict[str, Any]]):
        """Update right sidebar and file transfer dropdown with new users list."""
        self._online_users = users
        current_u = self.network_mgr.current_username

        # Filter out current user for sidebar display
        peer_users = [u for u in users if u["username"] != current_u]
        self.user_count_badge.configure(text=str(len(peer_users)))

        for widget in self.users_scroll.winfo_children():
            widget.destroy()

        if not peer_users:
            lbl = ctk.CTkLabel(
                self.users_scroll,
                text="Waiting for other users\nto join the LAN...",
                font=("Helvetica", 11),
                text_color=COLOR_TEXT_MUTED,
                justify="center"
            )
            lbl.pack(pady=40)
        else:
            for u in peer_users:
                uname = u["username"]
                ip_addr = u.get("ip", "LAN")

                user_btn = ctk.CTkButton(
                    self.users_scroll,
                    text=f"🟢 @{uname}\n   {ip_addr}",
                    font=("Helvetica", 12),
                    anchor="w",
                    fg_color=COLOR_CARD_SECONDARY,
                    hover_color="#334155",
                    text_color=COLOR_TEXT_PRIMARY,
                    height=46,
                    corner_radius=8,
                    command=lambda name=uname: self._select_peer(name)
                )
                user_btn.pack(fill="x", pady=3)

        # Notify file view to update dropdown
        self.file_view.update_online_users(users)

    def _select_peer(self, peer_username: str):
        """Open chat with the clicked peer."""
        self.switch_view("chat")
        self.chat_view.set_active_peer(peer_username)

    def _shortcut_send_file(self, peer_username: str):
        """Jump to File Sharing view with peer preselected."""
        self.switch_view("files")
        self.file_view.preselect_recipient(peer_username)

    def _on_incoming_chat(self, sender: str, text: str, timestamp: str):
        """Handle incoming chat message in real time."""
        self.chat_view.append_incoming_message(sender, text, timestamp)

    def _on_conn_changed(self, is_connected: bool, reason: str):
        """Handle connection state updates in bottom status bar."""
        if is_connected:
            self.conn_dot.configure(text_color=COLOR_SUCCESS)
            self.conn_text.configure(text=f"Connected ({reason})")
        else:
            self.conn_dot.configure(text_color=COLOR_DANGER)
            self.conn_text.configure(text=f"Disconnected: {reason}")

    def _on_security_alert(self, level: str, message: str):
        """Display security alert dialog."""
        color = COLOR_DANGER if level == "critical" else (COLOR_WARNING if level == "warning" else COLOR_PRIMARY)

        alert_win = ctk.CTkToplevel(self)
        alert_win.title("Security Notice")
        alert_win.geometry("400x180")
        alert_win.resizable(False, False)
        alert_win.attributes("-topmost", True)
        alert_win.configure(fg_color=COLOR_BG_DARK)

        content = ctk.CTkFrame(alert_win, fg_color=COLOR_CARD, corner_radius=12)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        icon_text = "🚨 Critical Security Alert" if level == "critical" else "ℹ️ System Notice"
        head = ctk.CTkLabel(content, text=icon_text, font=("Helvetica", 14, "bold"), text_color=color)
        head.pack(pady=(10, 10))

        msg_lbl = ctk.CTkLabel(content, text=message, font=("Helvetica", 11), text_color=COLOR_TEXT_PRIMARY, wraplength=340)
        msg_lbl.pack(pady=(0, 15))

        ok_btn = ctk.CTkButton(content, text="Dismiss", width=80, height=28, command=alert_win.destroy)
        ok_btn.pack()

    def _on_logout_click(self):
        """Log out and switch back to Login view."""
        self.network_mgr.logout()
        self.on_logout()
