import os
import shutil
import psutil
import tempfile
import customtkinter as ctk
import threading
import time
import ctypes
import webbrowser
import tkinter as tk
from tkinter import messagebox
from send2trash import send2trash

# ------------------------
# Helper Functions
# ------------------------
def get_free_space():
    total, used, free = shutil.disk_usage("C:\\")
    return round(free / (1024**3), 2)

def safe_delete(path):
    try:
        if os.path.isfile(path) or os.path.islink(path):
            send2trash(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True
    except:
        return False

def clean_directory(path, name="folder"):
    freed, failed = 0, 0
    if not os.path.exists(path):
        return freed, failed
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                fp = os.path.join(root, f)
                size = os.path.getsize(fp)
                if safe_delete(fp):
                    freed += size
                else:
                    failed += 1
            except:
                failed += 1
    if freed > 0:
        log_insert(f"✅ Freed {round(freed/1024/1024,2)} MB from {name}", "success")
    if failed > 0:
        log_insert(f"⚠️ {failed} files could not be deleted (system in use)", "warning")
    return freed, failed

def empty_recycle_bin():
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
        log_insert("✅ Recycle Bin emptied successfully", "success")
    except:
        log_insert("⚠️ Could not empty Recycle Bin (insufficient permissions)", "warning")

def system_stats():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    log_insert(f"📊 CPU: {cpu}% | RAM: {ram}%", "info")
    return cpu, ram

def clean_ram():
    log_insert("🧹 Cleaning RAM cache...", "info")
    try:
        ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
        log_insert("✅ App RAM cache cleaned", "success")
    except Exception as e:
        log_insert(f"⚠️ Failed to clean RAM: {e}", "warning")

def clean_downloads():
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.exists(downloads_path):
        log_insert("⚠️ Downloads folder not found", "warning")
        return
    freed, failed = clean_directory(downloads_path, "Downloads")
    log_insert(f"💾 Cleared {freed/1024/1024:.2f} MB from Downloads", "success")

# ------------------------
# UI Helpers
# ------------------------
def rgb_cycle_centered(widget, colors, delay=150, property_name="progress_color"):
    index = 0
    def cycle():
        nonlocal index
        try:
            widget.set(0.5)  # always center
            widget.configure(**{property_name: colors[index]})
        except:
            pass
        index = (index + 1) % len(colors)
        widget.after(delay, cycle)
    cycle()

def create_button(master, text, command, width=220, height=50, color="#a855f7"):
    container = ctk.CTkFrame(master, width=width, height=height+20, fg_color="#1a1a1a", corner_radius=15)
    container.pack_propagate(False)
    container.pack(pady=5)

    btn = ctk.CTkButton(container, text=text, command=command,
                        width=width, height=height,
                        fg_color=color, hover_color="#c084fc", text_color="white",
                        corner_radius=15, font=("Segoe UI", 15, "bold"))
    btn.pack(pady=(0,0))

    glow = tk.Canvas(container, width=width, height=15, highlightthickness=0, bg="#1a1a1a")
    glow.pack(pady=(0,0))
    rect = glow.create_rectangle(0,0,width,15, fill=color, outline="")

    alpha = 0
    direction = 1
    def animate_glow():
        nonlocal alpha, direction
        alpha += direction * 5
        if alpha > 100:
            alpha = 100
            direction = -1
        if alpha < 20:
            alpha = 20
            direction = 1
        r = int(int(color[1:3],16) * alpha/100)
        g = int(int(color[3:5],16) * alpha/100)
        b = int(int(color[5:7],16) * alpha/100)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        glow.itemconfig(rect, fill=hex_color)
        glow.after(50, animate_glow)
    animate_glow()

    def on_enter(e):
        btn.configure(width=width+10, height=height+3)
    def on_leave(e):
        btn.configure(width=width, height=height)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn

# ------------------------
# Log System
# ------------------------
log_filters = ["all"]

def log_insert(text, tag="info"):
    log_box.configure(state="normal")
    if "all" in log_filters or tag in log_filters:
        log_box.insert("end", f"{text}\n", tag)
        log_box.see("end")
    log_box.configure(state="disabled")

def update_log_filter():
    global log_filters
    if filter_vars["all"].get():
        log_filters = ["all"]
        for key,v in filter_vars.items():
            if key != "all":
                v.set(False)
    else:
        log_filters = [k for k,v in filter_vars.items() if v.get()]
    log_box.configure(state="normal")
    log_box.delete("1.0","end")
    log_box.configure(state="disabled")
    log_insert(f"🔹 Log filters updated: {', '.join(log_filters)}", "info")

# ------------------------
# Boost Functions
# ------------------------
def boost(premium=False):
    def task():
        log_box.configure(state="normal")
        log_box.delete("1.0","end")
        log_box.configure(state="disabled")
        progress.start()
        log_insert("🚀 Starting optimization...", "info")
        time.sleep(0.5)
        system_stats()
        time.sleep(0.5)

        clean_directory(tempfile.gettempdir(), "TEMP folders")
        empty_recycle_bin()
        clean_downloads()
        time.sleep(0.5)

        if premium:
            clean_directory(os.path.expanduser("~\\AppData\\Local\\Microsoft\\Windows\\INetCache"), "Cache")
            time.sleep(0.3)
            clean_directory(os.path.expanduser("~\\AppData\\Local\\Temp"), "AppData Temp")
            time.sleep(0.3)
            clean_directory("C:\\Windows\\Prefetch", "Prefetch cache")
            time.sleep(0.3)

        clean_ram()
        system_stats()
        log_insert("🎉 Optimization complete!", "success")
        progress.stop()
        messagebox.showinfo("Done", "Optimization complete!")
    threading.Thread(target=task, daemon=True).start()

# ------------------------
# GUI Setup
# ------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
root = ctk.CTk()
root.title("PC Booster 🚀")
root.geometry("950x750")
root.configure(fg_color="#0f0f0f")

# Title
title = ctk.CTkLabel(root, text="⚡ PC Booster 🚀", font=("Segoe UI",28,"bold"), text_color="white")
title.pack(pady=10)

# Log frame
log_frame = ctk.CTkFrame(root, corner_radius=15, fg_color="#1a1a1a")
log_frame.pack(padx=10, pady=10, fill="both", expand=False)

filter_frame = ctk.CTkFrame(log_frame, corner_radius=10, fg_color="#1a1a1a")
filter_frame.pack(pady=5, fill="x")

filter_vars = {
    "all": tk.BooleanVar(value=True),
    "success": tk.BooleanVar(value=False),
    "warning": tk.BooleanVar(value=False),
    "error": tk.BooleanVar(value=False),
    "premium": tk.BooleanVar(value=False),
    "info": tk.BooleanVar(value=False)
}

for key in ["all","success","warning","error","premium","info"]:
    cb = ctk.CTkCheckBox(filter_frame, text=key.capitalize(), variable=filter_vars[key],
                          command=update_log_filter, text_color="white", fg_color="#a855f7", hover_color="#c084fc")
    cb.pack(side="left", padx=5)

log_box = tk.Text(log_frame, width=100, height=15, bg="#1a1a1a", fg="white", font=("Segoe UI",11))
log_box.pack(padx=10,pady=10, fill="both", expand=True)
log_box.tag_config("success", foreground="#22c55e")
log_box.tag_config("warning", foreground="#facc15")
log_box.tag_config("error", foreground="#ef4444")
log_box.tag_config("premium", foreground="#c084fc")
log_box.tag_config("info", foreground="white")
log_box.configure(state="disabled")

# Boost / Premium section
top_frame = ctk.CTkFrame(root, corner_radius=15, fg_color="#1a1a1a")
top_frame.pack(pady=20)

code_entry = ctk.CTkEntry(top_frame, placeholder_text="Enter code", width=200)
code_entry.pack(side="left", padx=5)

def activate_premium():
    code = code_entry.get().strip()
    if code == "8791-gbdo":
        log_insert("🌟 PREMIUM features unlocked!", "premium")
        boost(premium=True)
    else:
        messagebox.showerror("Error", "❌ Invalid code!")

premium_button = create_button(top_frame, "Premium Boost", activate_premium)
premium_button.pack(side="left", padx=10)

boost_button = create_button(root, "Run Boost", lambda: boost(premium=False))
boost_button.pack(pady=20)

# Progress bar
progress = ctk.CTkProgressBar(root, mode="indeterminate", width=600, progress_color="#a855f7")
progress.pack(pady=15)
rgb_cycle_centered(progress, ["#ff0000","#00ff00","#0000ff"], 200)

# Discord button
def open_discord():
    webbrowser.open("https://discord.gg/gvEbhcb7Rk")

discord_button = create_button(root, "💬 Join Discord", open_discord, width=250, height=45, color="#9333ea")
discord_button.pack(pady=10)

root.mainloop()
