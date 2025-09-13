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
# Pomocné funkce
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

def clean_directory(path, name="složka"):
    if not os.path.exists(path):
        return 0, 0
    freed = 0
    failed = 0
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
        log_insert(f"✅ Uvolněno {round(freed/1024/1024,2)} MB z {name}")
    if failed > 0:
        log_insert(f"⚠️ {failed} souborů nelze smazat (používá je systém)")
    return freed, failed

def empty_recycle_bin():
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
        log_insert("✅ Koš úspěšně vyprázdněn")
    except:
        log_insert("⚠️ Nelze vyčistit koš (nedostatečná oprávnění)")

def system_stats():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    log_insert(f"📊 CPU: {cpu}% | RAM: {ram}%")

# ------------------------
# RAM čistič
# ------------------------
def clean_ram(all_processes=False):
    log_insert("🧹 Čištění RAM cache...")
    try:
        if all_processes:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, proc.info['pid'])
                    if handle:
                        ctypes.windll.kernel32.SetProcessWorkingSetSize(handle, -1, -1)
                        ctypes.windll.kernel32.CloseHandle(handle)
                except:
                    continue
            log_insert("🌟 PREMIUM: RAM všech procesů byla vyčištěna")
        else:
            ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
            log_insert("✅ RAM cache aplikace byla vyčištěna")
    except Exception as e:
        log_insert(f"⚠️ RAM se nepodařilo vyčistit: {e}")

# ------------------------
# Boost funkce
# ------------------------
def boost(premium=False):
    log_box.delete("1.0", "end")
    log_insert("🚀 Spouštím optimalizaci...\n---------------------------")
    progress.start()

    before = get_free_space()
    system_stats()

    clean_directory(tempfile.gettempdir(), "TEMP složky")
    empty_recycle_bin()

    if premium:
        clean_directory(os.path.expanduser("~\\AppData\\Local\\Microsoft\\Windows\\INetCache"), "Cache")
        clean_directory(os.path.expanduser("~\\AppData\\Local\\Temp"), "AppData Temp")
        clean_directory("C:\\Windows\\Prefetch", "Prefetch cache")

    after = get_free_space()
    freed = round(after - before, 2)
    if freed > 0:
        log_insert(f"💾 Celkem uvolněno {freed} GB")

    clean_ram(all_processes=premium)

    system_stats()
    if premium:
        log_insert("🌟 PREMIUM BOOST dokončen – hlubší úklid hotov!")
    else:
        log_insert("🎉 Optimalizace dokončena!")

    progress.stop()
    messagebox.showinfo("Hotovo", f"Optimalizace dokončena!\nUvolněno: {freed} GB")

# ------------------------
# Premium funkce
# ------------------------
premium_active = False

def premium_loop():
    while premium_active:
        boost(premium=True)
        time.sleep(600)  # každých 10 minut

def activate_premium():
    global premium_active
    code = code_entry.get().strip()
    if code == "8791-gbdo":
        premium_active = True
        premium_banner.pack(pady=5)
        log_insert("🌟 PREMIUM funkce odemknuty – automatický BOOST každých 10 minut!")
        threading.Thread(target=premium_loop, daemon=True).start()
    else:
        messagebox.showerror("Chyba", "❌ Neplatný kód!")

# ------------------------
# GUI pomocí customtkinter
# ------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("PC-Uklízečka 🚀")
root.geometry("850x650")

# Titulek
title = ctk.CTkLabel(root, text="⚡ PC-Uklízečka 🚀", 
                     font=("Segoe UI", 28, "bold"), text_color="#a855f7")
title.pack(pady=15)

# Premium banner
premium_banner = ctk.CTkLabel(root, text="🌟 PREMIUM AKTIVNÍ 🌟", 
                              font=("Segoe UI", 16, "bold"), 
                              text_color="#c084fc")

# ------------------------
# Animace tlačítek
# ------------------------
def animate_button(btn, target_w, target_h, steps=6, delay=15):
    current_w = btn.cget("width")
    current_h = btn.cget("height")
    dw = (target_w - current_w) / steps
    dh = (target_h - current_h) / steps

    def step(i=0):
        if i < steps:
            btn.configure(width=int(current_w + dw * (i+1)),
                          height=int(current_h + dh * (i+1)))
            btn.after(delay, step, i+1)
    step()

def create_hover_button(master, text, command, width=200, height=40):
    btn = ctk.CTkButton(master, text=text, command=command,
                        fg_color="#a855f7", hover_color="#c084fc",
                        corner_radius=20, width=width, height=height, font=("Segoe UI", 15, "bold"))
    def on_enter(e):
        animate_button(btn, width+20, height+5)
    def on_leave(e):
        animate_button(btn, width, height)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

# ------------------------
# Premium panel
# ------------------------
top_frame = ctk.CTkFrame(root, corner_radius=15)
top_frame.pack(pady=10)

code_entry = ctk.CTkEntry(top_frame, placeholder_text="Zadej premium kód", width=200)
code_entry.pack(side="left", padx=10, pady=10)

premium_button = create_hover_button(top_frame, "Aktivovat Premium", activate_premium)
premium_button.pack(side="left", padx=10)

# Boost tlačítko
boost_button = create_hover_button(root, "Spustit Úklid", lambda: boost(False),
                                   width=220, height=50)
boost_button.pack(pady=20)

# Progress bar
progress = ctk.CTkProgressBar(root, mode="indeterminate", width=600)
progress.pack(pady=15)

# ------------------------
# Barevná konzole log
# ------------------------
log_box = tk.Text(root, width=100, height=20, bg="#1f2937", fg="white", font=("Consolas", 11))
log_box.pack(padx=10, pady=10, fill="both", expand=True)

log_box.tag_config("success", foreground="#22c55e")   # zelená
log_box.tag_config("warning", foreground="#facc15")   # žlutá
log_box.tag_config("error", foreground="#ef4444")     # červená
log_box.tag_config("premium", foreground="#c084fc")   # fialová
log_box.tag_config("info", foreground="white")        # standardní

def log_insert(text):
    if "✅" in text:
        tag = "success"
    elif "⚠️" in text:
        tag = "warning"
    elif "❌" in text:
        tag = "error"
    elif "🌟" in text:
        tag = "premium"
    else:
        tag = "info"

    log_box.insert("end", f"{text}\n", tag)
    log_box.see("end")
    root.update()

# Discord odkaz
def open_discord():
    webbrowser.open("https://discord.gg/gvEbhcb7Rk")

discord = create_hover_button(root, "💬 Připoj se na Discord", open_discord,
                              width=250, height=45)
discord.configure(fg_color="#1e293b", hover_color="#a855f7")
discord.pack(pady=10)

root.mainloop()
