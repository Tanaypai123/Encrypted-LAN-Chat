"""
Main Application Entry Point.
Encrypted LAN Chat & File Sharing System (GUI)
Student: Tanay Sharma (ID: 23ESKCY051)
Group: CSL-G56
Subject Code: 23ESKCY051
"""

import sys
import argparse
import time
import customtkinter as ctk

from config import (
    APP_NAME,
    APP_VERSION,
    THEME_MODE,
    DEFAULT_PORT,
    COLOR_BG_DARK,
    get_local_ip
)
from app.network_manager import NetworkManager
from gui.login import LoginFrame
from gui.register import RegisterFrame
from gui.dashboard import DashboardFrame

class EncryptedLANChatApp(ctk.CTk):
    """Main Application Window managing high-level screen navigation."""

    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1120x740")
        self.minsize(980, 640)
        self.configure(fg_color=COLOR_BG_DARK)

        # Set Global CustomTkinter Theme
        ctk.set_appearance_mode(THEME_MODE)
        ctk.set_default_color_theme("blue")

        # Core Network and State Orchestrator
        self.network_mgr = NetworkManager()

        # Navigation State Container
        self.current_screen: ctk.CTkFrame = None

        # Clean Exit Protocol
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Start on Login Screen
        self.show_login_screen()

    def show_login_screen(self):
        """Display the Login View."""
        if self.current_screen:
            self.current_screen.destroy()

        self.current_screen = LoginFrame(
            self,
            network_mgr=self.network_mgr,
            on_login_success=self.show_dashboard_screen,
            on_switch_to_register=self.show_register_screen,
            on_open_server_modal=self._quick_launch_local_server
        )
        self.current_screen.pack(fill="both", expand=True)

    def show_register_screen(self):
        """Display the Registration View."""
        if self.current_screen:
            self.current_screen.destroy()

        self.current_screen = RegisterFrame(
            self,
            network_mgr=self.network_mgr,
            on_register_success=self.show_login_screen,
            on_switch_to_login=self.show_login_screen
        )
        self.current_screen.pack(fill="both", expand=True)

    def show_dashboard_screen(self, username: str):
        """Display the Main Workspace Dashboard View."""
        if self.current_screen:
            self.current_screen.destroy()

        self.current_screen = DashboardFrame(
            self,
            network_mgr=self.network_mgr,
            on_logout=self.show_login_screen
        )
        self.current_screen.pack(fill="both", expand=True)

    def _quick_launch_local_server(self):
        """Helper to quickly start local server from login screen."""
        started = self.network_mgr.start_server(DEFAULT_PORT)
        if started:
            ip = get_local_ip()
            dialog = ctk.CTkToplevel(self)
            dialog.title("Server Started")
            dialog.geometry("380x160")
            dialog.attributes("-topmost", True)
            dialog.configure(fg_color=COLOR_BG_DARK)

            lbl = ctk.CTkLabel(
                dialog,
                text=f"✅ LAN Server Started Successfully!\n\n"
                     f"Your LAN IP: {ip}\nPort: {DEFAULT_PORT}\n\n"
                     f"Other peers can now connect to this IP.",
                font=("Helvetica", 12),
                justify="center"
            )
            lbl.pack(pady=20)
            btn = ctk.CTkButton(dialog, text="OK", width=80, command=dialog.destroy)
            btn.pack()

    def _on_closing(self):
        """Handle window close event with clean network teardown."""
        try:
            self.network_mgr.logout()
        except Exception:
            pass

        try:
            self.network_mgr.stop_server()
        except Exception:
            pass

        self.destroy()

def run_standalone_server(port: int):
    """Run dedicated headless TCP server from CLI."""
    print("=" * 60)
    print(f"Encrypted LAN Chat Server - Dedicated Mode")
    print(f"Student: Tanay Sharma (23ESKCY051, CSL-G56)")
    print("=" * 60)

    mgr = NetworkManager()
    started = mgr.start_server(port)
    if started:
        ip = get_local_ip()
        print(f"[+] Server successfully listening on 0.0.0.0:{port}")
        print(f"[+] LAN IP: {ip}")
        print(f"[+] Press Ctrl+C to terminate server.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Shutting down server...")
            mgr.stop_server()
            print("[+] Server stopped cleanly.")
    else:
        print("[-] Failed to start server. Port may be in use.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Encrypted LAN Chat & File Sharing")
    parser.add_argument("--server", action="store_true", help="Run in dedicated headless server mode")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to listen on or connect to")
    args = parser.parse_args()

    if args.server:
        run_standalone_server(args.port)
    else:
        app = EncryptedLANChatApp()
        app.mainloop()

if __name__ == "__main__":
    main()
