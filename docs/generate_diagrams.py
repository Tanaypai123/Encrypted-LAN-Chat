"""
Asset Generator for Cyber Security Lab Mini Project Report.
Generates labeled figures and diagrams matching RTU/SKIT syllabus requirements.
Author: Tanay Sharma (23ESKCY051, CSL-G56)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

docs_dir = Path("docs")
docs_dir.mkdir(exist_ok=True)

# 1. Figure: Test Results Chart
plt.figure(figsize=(7, 3.2), dpi=200)
categories = ['Authentication', 'Cryptography', 'Key Exchange', 'Networking', 'Protocol Framing', 'File Transfer']
passed_counts = [7, 7, 2, 4, 3, 4]
colors_list = ['#3B82F6', '#8B5CF6', '#10B981', '#06B6D4', '#F59E0B', '#EC4899']

bars = plt.bar(categories, passed_counts, color=colors_list, width=0.55, edgecolor='#1E293B', linewidth=1)
plt.title('Automated Test Execution Summary: 27/27 Tests Passed (100%)', fontsize=11, fontweight='bold', pad=12, color='#0F172A')
plt.xlabel('Subsystem / Module Tested', fontsize=9.5, fontweight='bold', color='#1E293B')
plt.ylabel('Number of Test Cases', fontsize=9.5, fontweight='bold', color='#1E293B')
plt.ylim(0, 9)
plt.grid(axis='y', linestyle='--', alpha=0.5)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.25, f"{int(yval)} Passed", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#0F172A')

plt.tight_layout()
plt.savefig(docs_dir / "fig_test_results.png")
plt.close()

# 2. Figure: Network Topology Diagram
fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=200)
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

# Router
router_box = patches.FancyBboxPatch((3.8, 4.4), 2.4, 1.2, boxstyle="round,pad=0.2", ec="#1E293B", fc="#1E1B4B", lw=1.5)
ax.add_patch(router_box)
ax.text(5.0, 5.2, "Wi-Fi Router / Switch", ha="center", va="center", color="#FFFFFF", fontsize=10, fontweight="bold")
ax.text(5.0, 4.7, "LAN Subnet: 192.168.1.0/24", ha="center", va="center", color="#A5B4FC", fontsize=8)

# Host A
host_a = patches.FancyBboxPatch((0.5, 0.8), 3.4, 2.4, boxstyle="round,pad=0.2", ec="#2563EB", fc="#0B0F19", lw=1.5)
ax.add_patch(host_a)
ax.text(2.2, 2.7, "Workstation A (Host)", ha="center", va="center", color="#60A5FA", fontsize=10, fontweight="bold")
ax.text(2.2, 2.2, "LAN IP: 192.168.1.50\nPort: 55555 (TCP Server)\nUser: @alice (Client A)", ha="center", va="center", color="#F8FAFC", fontsize=8)
ax.text(2.2, 1.3, "State: [ONLINE] (Host + Client)", ha="center", va="center", color="#10B981", fontsize=7.5, fontweight="bold")

# Host B
host_b = patches.FancyBboxPatch((6.1, 0.8), 3.4, 2.4, boxstyle="round,pad=0.2", ec="#7C3AED", fc="#0B0F19", lw=1.5)
ax.add_patch(host_b)
ax.text(7.8, 2.7, "Workstation B (Client)", ha="center", va="center", color="#C084FC", fontsize=10, fontweight="bold")
ax.text(7.8, 2.2, "LAN IP: 192.168.1.75\nClient Socket -> 55555\nUser: @bob (Client B)", ha="center", va="center", color="#F8FAFC", fontsize=8)
ax.text(7.8, 1.3, "State: [ONLINE] (Client)", ha="center", va="center", color="#10B981", fontsize=7.5, fontweight="bold")

# Arrows
ax.annotate("", xy=(5.0, 4.3), xytext=(2.2, 3.4), arrowprops=dict(arrowstyle="<->", color="#3B82F6", lw=1.5))
ax.annotate("", xy=(5.0, 4.3), xytext=(7.8, 3.4), arrowprops=dict(arrowstyle="<->", color="#8B5CF6", lw=1.5))

# End to End Line
ax.annotate("", xy=(6.0, 2.0), xytext=(4.0, 2.0), arrowprops=dict(arrowstyle="<->", color="#10B981", lw=2, ls="--"))
ax.text(5.0, 2.25, "[SECURE] AES-256-GCM + X25519", ha="center", va="center", color="#10B981", fontsize=8, fontweight="bold")
ax.text(5.0, 1.75, "E2E Encrypted Payload", ha="center", va="center", color="#64748B", fontsize=7.5)

plt.tight_layout()
plt.savefig(docs_dir / "fig_network_topology.png")
plt.close()

# 3. Figure: Cryptographic Protocol Pipeline
fig, ax = plt.subplots(figsize=(7.5, 3.2), dpi=200)
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)
ax.axis('off')

# Steps boxes
b1 = patches.FancyBboxPatch((0.4, 1.2), 1.8, 1.8, boxstyle="round,pad=0.15", ec="#3B82F6", fc="#EFF6FF", lw=1.2)
ax.add_patch(b1)
ax.text(1.3, 2.5, "1. Key Agreement", ha="center", va="center", color="#1E3A8A", fontsize=8.5, fontweight="bold")
ax.text(1.3, 1.9, "Curve25519\nX25519 ECDH\nEphemeral Keypair", ha="center", va="center", color="#1E293B", fontsize=7.5)

b2 = patches.FancyBboxPatch((2.7, 1.2), 1.8, 1.8, boxstyle="round,pad=0.15", ec="#8B5CF6", fc="#F5F3FF", lw=1.2)
ax.add_patch(b2)
ax.text(3.6, 2.5, "2. Key Derivation", ha="center", va="center", color="#581C87", fontsize=8.5, fontweight="bold")
ax.text(3.6, 1.9, "HKDF-SHA256\nContext: lan-chat-v1\n32-Byte Secret", ha="center", va="center", color="#1E293B", fontsize=7.5)

b3 = patches.FancyBboxPatch((5.0, 1.2), 2.0, 1.8, boxstyle="round,pad=0.15", ec="#10B981", fc="#ECFDF5", lw=1.2)
ax.add_patch(b3)
ax.text(6.0, 2.5, "3. AEAD Cipher", ha="center", va="center", color="#064E3B", fontsize=8.5, fontweight="bold")
ax.text(6.0, 1.9, "AES-256-GCM\n96-bit Nonce (os.urandom)\n128-bit Tag", ha="center", va="center", color="#1E293B", fontsize=7.5)

b4 = patches.FancyBboxPatch((7.5, 1.2), 2.1, 1.8, boxstyle="round,pad=0.15", ec="#F59E0B", fc="#FFFBEB", lw=1.2)
ax.add_patch(b4)
ax.text(8.55, 2.5, "4. Verification", ha="center", va="center", color="#78350F", fontsize=8.5, fontweight="bold")
ax.text(8.55, 1.9, "Tag Verification\nSHA-256 File Checksum\nPath Sanitizer", ha="center", va="center", color="#1E293B", fontsize=7.5)

# Connectors
ax.annotate("", xy=(2.6, 2.1), xytext=(2.3, 2.1), arrowprops=dict(arrowstyle="->", color="#1E293B", lw=1.5))
ax.annotate("", xy=(4.9, 2.1), xytext=(4.6, 2.1), arrowprops=dict(arrowstyle="->", color="#1E293B", lw=1.5))
ax.annotate("", xy=(7.4, 2.1), xytext=(7.1, 2.1), arrowprops=dict(arrowstyle="->", color="#1E293B", lw=1.5))

plt.tight_layout()
plt.savefig(docs_dir / "fig_crypto_flow.png")
plt.close()

# 4. Figure: GUI Interface Screenshot / Mockup Card
fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=200)
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

# Window frame
win = patches.FancyBboxPatch((0.2, 0.2), 9.6, 5.6, boxstyle="round,pad=0.1", ec="#374151", fc="#0B0F19", lw=1.5)
ax.add_patch(win)

# Title bar
title_bar = patches.Rectangle((0.2, 5.3), 9.6, 0.5, fc="#111827")
ax.add_patch(title_bar)
ax.text(0.5, 5.55, "Encrypted LAN Chat & File Sharing v1.0.0", color="#F8FAFC", fontsize=8, va="center")
ax.text(9.5, 5.55, "[E2E Active: AES-256-GCM / X25519]", color="#818CF8", fontsize=7.5, fontweight="bold", ha="right", va="center")

# Left Sidebar
sidebar = patches.Rectangle((0.2, 0.6), 2.2, 4.7, fc="#111827")
ax.add_patch(sidebar)
ax.text(0.4, 4.9, "LAN Encrypted Hub", color="#FFFFFF", fontsize=8.5, fontweight="bold")
nav_items = ["Encrypted Chat", "File Transfer", "LAN Server", "History Logs", "Settings"]
for i, item in enumerate(nav_items):
    fc = "#2563EB" if i == 0 else "#1F2937"
    nb = patches.Rectangle((0.3, 4.3 - i*0.55), 2.0, 0.45, fc=fc)
    ax.add_patch(nb)
    ax.text(0.4, 4.52 - i*0.55, item, color="#FFFFFF", fontsize=7.5, va="center")

# Center Chat Canvas
canvas_bg = patches.Rectangle((2.4, 1.2), 5.4, 4.1, fc="#0F172A")
ax.add_patch(canvas_bg)
header_box = patches.Rectangle((2.4, 4.8), 5.4, 0.5, fc="#1E293B")
ax.add_patch(header_box)
ax.text(2.6, 5.05, "@bob (Online)", color="#F8FAFC", fontsize=8, fontweight="bold", va="center")
ax.text(7.6, 5.05, "[E2E Encrypted]", color="#10B981", fontsize=7.5, fontweight="bold", ha="right", va="center")

# Chat bubbles
b_in1 = patches.FancyBboxPatch((2.6, 4.1), 3.2, 0.55, boxstyle="round,pad=0.08", fc="#1E293B")
ax.add_patch(b_in1)
ax.text(2.75, 4.37, "Hello Alice! LAN connection established.", color="#F8FAFC", fontsize=7)

b_out1 = patches.FancyBboxPatch((4.4, 3.35), 3.2, 0.55, boxstyle="round,pad=0.08", fc="#2563EB")
ax.add_patch(b_out1)
ax.text(4.55, 3.62, "Hi Bob! This message is E2E encrypted.", color="#FFFFFF", fontsize=7)

b_in2 = patches.FancyBboxPatch((2.6, 2.6), 3.4, 0.55, boxstyle="round,pad=0.08", fc="#1E293B")
ax.add_patch(b_in2)
ax.text(2.75, 2.87, "Sending project_archive.zip (SHA-256 OK).", color="#F8FAFC", fontsize=7)

# Message input bar
inp_bg = patches.Rectangle((2.4, 0.6), 5.4, 0.6, fc="#111827")
ax.add_patch(inp_bg)
inp_box = patches.Rectangle((2.6, 0.7), 4.1, 0.4, fc="#1F2937", ec="#374151")
ax.add_patch(inp_box)
ax.text(2.8, 0.9, "Type a secure message to @bob...", color="#94A3B8", fontsize=7)
send_btn = patches.Rectangle((6.8, 0.7), 0.9, 0.4, fc="#2563EB")
ax.add_patch(send_btn)
ax.text(7.25, 0.9, "Send", color="#FFFFFF", fontsize=7, fontweight="bold", ha="center")

# Right Sidebar (Online Users)
right_sidebar = patches.Rectangle((7.8, 0.6), 2.0, 4.7, fc="#111827")
ax.add_patch(right_sidebar)
ax.text(8.0, 4.9, "Online Users (1)", color="#F8FAFC", fontsize=8, fontweight="bold")
user_pill = patches.Rectangle((7.9, 4.2), 1.8, 0.55, fc="#1E293B")
ax.add_patch(user_pill)
ax.text(8.0, 4.47, "[*] @bob", color="#F8FAFC", fontsize=7.5, fontweight="bold")
ax.text(8.0, 4.3, "    192.168.1.75", color="#94A3B8", fontsize=6.5)

# Bottom Status bar
bot_bar = patches.Rectangle((0.2, 0.2), 9.6, 0.4, fc="#111827")
ax.add_patch(bot_bar)
ax.text(0.4, 0.4, "[Online] Connected to 192.168.1.50:55555", color="#10B981", fontsize=7, va="center")
ax.text(5.0, 0.4, "Logged in as: @alice", color="#818CF8", fontsize=7, fontweight="bold", ha="center", va="center")
ax.text(9.5, 0.4, "[Encrypted] AES-256-GCM / X25519", color="#A5B4FC", fontsize=7, ha="right", va="center")

plt.tight_layout()
plt.savefig(docs_dir / "fig_gui_chat.png")
plt.close()

print("[+] All diagram assets generated successfully in docs/")
