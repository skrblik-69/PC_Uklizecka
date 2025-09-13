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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

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
        cpu, ram = system_stats()
        update_cpu_ram_chart(cpu, ram)
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
root.geometry("1000x850")
root.configure(fg_color="#0f0f0f")  # černé pozadí

# Title
title = ctk.CTkLabel(root, text="⚡ PC Booster 🚀", font=("Segoe UI",28,"bold"), text_color="white")
title.pack(pady=10)

# ------------------------
# Function to create under-glow
# ------------------------
def create_under_glow(widget, color="#a855f7", height=15):
    """Creates a subtle under-glow gradient below a widget."""
    # Make sure widget update to get width
    widget.update()
    width = widget.winfo_width()
    glow = tk.Canvas(widget.master, width=width, height=height, highlightthickness=0, bg="#0f0f0f")
    glow.pack(after=widget)
    # Draw gradient
    steps = height
    for i in range(steps):
        alpha = int(255 * (1 - i/steps))
        hex_color = f"#{alpha:02x}{int(alpha*0.65):02x}{int(alpha*1.0):02x}"  # gradient fialová
        glow.create_line(0, i, width, i, fill=color)
    widget.lift()
    return glow

# Premium Banner (hidden)
banner_container = ctk.CTkFrame(root, width=400, height=50, corner_radius=20, fg_color="#111827")
banner_container.pack(pady=5)
premium_banner = ctk.CTkLabel(banner_container, text="🌟 PREMIUM ACTIVE 🌟", font=("Segoe UI",18,"bold"), fg_color="#111827", text_color="white")
premium_banner.pack_forget()

# Log frame
log_frame = ctk.CTkFrame(root, corner_radius=15, fg_color="#1a1a1a")
log_frame.pack(padx=10,pady=10, fill="both", expand=False)

# Filter checkboxes
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

# Log box
log_box = tk.Text(log_frame, width=100, height=15, bg="#1a1a1a", fg="white", font=("Segoe UI",11))
log_box.pack(padx=10,pady=10, fill="both", expand=True)
log_box.tag_config("success", foreground="#22c55e")
log_box.tag_config("warning", foreground="#facc15")
log_box.tag_config("error", foreground="#ef4444")
log_box.tag_config("premium", foreground="#c084fc")
log_box.tag_config("info", foreground="white")
log_box.configure(state="disabled")

# Top frame for code input + premium boost
top_frame = ctk.CTkFrame(root, corner_radius=15, fg_color="#1a1a1a")
top_frame.pack(pady=10)

code_entry = ctk.CTkEntry(top_frame, placeholder_text="Enter code", width=200)
code_entry.pack(side="left", padx=5, pady=5)

def activate_premium():
    code = code_entry.get().strip()
    if code == "8791-gbdo":
        premium_banner.pack(expand=True, fill="both")
        create_under_glow(premium_banner, color="#c084fc", height=15)
        log_insert("🌟 PREMIUM features unlocked!", "premium")
        boost(normal=True, premium=True)
    else:
        messagebox.showerror("Error", "❌ Invalid code!")

premium_button = ctk.CTkButton(top_frame, text="Premium Boost", command=activate_premium,
                               width=200, height=50, fg_color="#a855f7", hover_color="#c084fc", text_color="white")
premium_button.pack(side="left", padx=10)
create_under_glow(premium_button)

# Normal Boost
boost_button = ctk.CTkButton(root, text="Run Boost", command=lambda: boost(normal=True),
                             width=250, height=60, fg_color="#a855f7", hover_color="#c084fc", text_color="white")
boost_button.pack(pady=20)
create_under_glow(boost_button)

# Progress bar
progress = ctk.CTkProgressBar(root, mode="indeterminate", width=700)
progress.pack(pady=10)

# ------------------------
# CPU/RAM Chart
# ------------------------
fig = Figure(figsize=(8,2.5), dpi=100)
ax = fig.add_subplot(111)
ax.set_ylim(0,100)
ax.set_title("CPU / RAM Usage", color="white")
ax.set_ylabel("%", color="white")
ax.set_xlabel("Metric", color="white")
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
bars = ax.bar(["CPU","RAM"], [0,0], color=["#ff0000","#00ff00"])
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=10)

def update_cpu_ram_chart(cpu, ram):
    bars[0].set_height(cpu)
    bars[1].set_height(ram)
    canvas.draw()

# Discord button
discord_button = ctk.CTkButton(root, text="💬 Join Discord", command=lambda: webbrowser.open("https://discord.gg/gvEbhcb7Rk"),
                               width=220, height=50, fg_color="#a855f7", hover_color="#c084fc", text_color="white")
discord_button.pack(pady=10)
create_under_glow(discord_button)

root.mainloop()
