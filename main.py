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

# ------------------------
# Helper Functions
# ------------------------
def get_free_space():
    total, used, free = shutil.disk_usage("C:\\")
    return round(free / (1024**3), 2)

def safe_delete(path):
    try:
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
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

def clean_ram():
    log_insert("🧹 Cleaning RAM cache...", "info")
    try:
        ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
        log_insert("✅ App RAM cache cleaned", "success")
    except Exception as e:
        log_insert(f"⚠️ Failed to clean RAM: {e}", "warning")

# ------------------------
# GUI Helpers
# ------------------------
def rgb_cycle(widget, colors, delay=150, property_name="text_color"):
    index = 0
    def cycle():
        nonlocal index
        try:
            if property_name == "text_color":
                widget.configure(text_color=colors[index])
            elif property_name == "progress_color":
                widget.configure(progress_color=colors[index])
            else:
                widget.configure(fg_color=colors[index])
        except:
            pass
        index = (index + 1) % len(colors)
        widget.after(delay, cycle)
    cycle()

def create_button_with_glow(master, text, command, width=220, height=50, glow_color="#a855f7"):
    container = ctk.CTkFrame(master, width=width, height=height+20, corner_radius=25, fg_color="#1f2937")
    container.pack_propagate(False)
    container.pack(pady=5)

    canvas = tk.Canvas(container, width=width, height=height+20, highlightthickness=0, bg="#1f2937")
    canvas.place(x=0, y=0)

    for i in range(15):
        canvas.create_rectangle(0, i, width, i+1, fill=glow_color, outline="")

    btn = ctk.CTkButton(container, text=text, command=command,
                        fg_color="#111827", hover_color="#1f2937",
                        width=width, height=height, corner_radius=20,
                        font=("Segoe UI", 15, "bold"))
    btn.place(x=0, y=10)
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
def boost(normal=True, premium=False):
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
        time.sleep(0.3)
        empty_recycle_bin()
        time.sleep(0.3)

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
root.geometry("900x800")

# Title
title = ctk.CTkLabel(root, text="⚡ PC Booster 🚀", font=("Segoe UI",28,"bold"))
title.pack(pady=10)

# Premium Banner with glow (hidden initially)
banner_container = ctk.CTkFrame(root, width=400, height=50, corner_radius=20, fg_color="#111827")
banner_container.pack(pady=5)
canvas_banner = tk.Canvas(banner_container, width=400, height=50, highlightthickness=0, bg="#111827")
canvas_banner.place(x=0, y=0)
for i in range(15):
    canvas_banner.create_rectangle(0, i, 400, i+1, fill="#ff00ff", outline="")
premium_banner = ctk.CTkLabel(banner_container, text="🌟 PREMIUM ACTIVE 🌟", font=("Segoe UI",18,"bold"), fg_color="#111827")
premium_banner.pack_forget()  # hidden initially

# Log frame
log_frame = ctk.CTkFrame(root, corner_radius=15)
log_frame.pack(padx=10,pady=10, fill="both", expand=False)

# Filter checkboxes
filter_frame = ctk.CTkFrame(log_frame, corner_radius=10)
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
                          command=update_log_filter)
    cb.pack(side="left", padx=5)

# Log box
log_box = tk.Text(log_frame, width=100, height=15, bg="#1f2937", fg="white", font=("Consolas",11))
log_box.pack(padx=10,pady=10, fill="both", expand=True)
log_box.tag_config("success", foreground="#22c55e")
log_box.tag_config("warning", foreground="#facc15")
log_box.tag_config("error", foreground="#ef4444")
log_box.tag_config("premium", foreground="#c084fc")
log_box.tag_config("info", foreground="white")
log_box.configure(state="disabled")

# Top frame for code input + premium boost
top_frame = ctk.CTkFrame(root, corner_radius=15)
top_frame.pack(pady=10)

code_entry = ctk.CTkEntry(top_frame, placeholder_text="Enter code", width=200)
code_entry.pack(side="left", padx=5, pady=5)

def activate_premium():
    code = code_entry.get().strip()
    if code == "8791-gbdo":
        premium_banner.pack(expand=True, fill="both")
        log_insert("🌟 PREMIUM features unlocked!", "premium")
        boost(premium=True)
    else:
        messagebox.showerror("Error", "❌ Invalid code!")

premium_button = create_button_with_glow(top_frame, "Premium Boost", activate_premium, width=200, height=50, glow_color="#ff00ff")
premium_button.pack(side="left", padx=10)

# Normal Boost
boost_button = create_button_with_glow(root, "Run Boost", lambda: boost(normal=True), width=250, height=60, glow_color="#a855f7")
boost_button.pack(pady=20)

# Progress bar
progress = ctk.CTkProgressBar(root, mode="indeterminate", width=700)
progress.pack(pady=10)
rgb_cycle(progress, ["#ff0000","#00ff00","#0000ff"],150,property_name="progress_color")

# Discord button
discord_button = create_button_with_glow(root, "💬 Join Discord", lambda: webbrowser.open("https://discord.gg/gvEbhcb7Rk"), width=220, height=50, glow_color="#22c55e")
discord_button.pack(pady=10)

root.mainloop()
