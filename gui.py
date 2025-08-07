import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
import requests
import threading

STORAGE_DIR = 'storage'
CONFIG_FILE = 'config.json'

os.makedirs(STORAGE_DIR, exist_ok=True)

with open(CONFIG_FILE) as f:
    NODES = json.load(f)['nodes']

class BackupGUI:
    def __init__(self, master):
        self.master = master
        master.title("📁 Distributed File Backup System")
        master.geometry("650x500")

        # Buttons
        self.upload_btn = tk.Button(master, text="➕ Add File", width=20, command=self.upload_file)
        self.upload_btn.grid(row=0, column=0, padx=10, pady=5)

        self.delete_btn = tk.Button(master, text="🗑️ Delete File", width=20, command=self.delete_file)
        self.delete_btn.grid(row=0, column=1, padx=10, pady=5)

        self.sync_btn = tk.Button(master, text="🔁 Sync Now", width=20, command=self.sync_now)
        self.sync_btn.grid(row=0, column=2, padx=10, pady=5)

        self.refresh_btn = tk.Button(master, text="🔄 Refresh Files", width=20, command=self.view_files)
        self.refresh_btn.grid(row=1, column=0, columnspan=3, pady=5)

        # Listbox to display files
        self.file_listbox = tk.Listbox(master, width=70, height=10)
        self.file_listbox.grid(row=2, column=0, columnspan=3, padx=10)

        # Log output
        self.output = scrolledtext.ScrolledText(master, height=15, width=80)
        self.output.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        self.log("App started.")
        self.view_files()

    def log(self, msg):
        self.output.insert(tk.END, f"{msg}\n")
        self.output.see(tk.END)

    def upload_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        filename = os.path.basename(path)
        try:
            with open(path, 'rb') as f:
                data = f.read()
            with open(os.path.join(STORAGE_DIR, filename), 'wb') as out:
                out.write(data)
            self.log(f"Added '{filename}' to local storage.")
            self.view_files()
        except Exception as e:
            messagebox.showerror("Error", f"Upload failed: {e}")

    def delete_file(self):
        selected = self.file_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a file to delete.")
            return
        filename = self.file_listbox.get(selected[0])
        try:
            os.remove(os.path.join(STORAGE_DIR, filename))
            self.log(f"Deleted '{filename}' from local storage.")
            self.view_files()
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed: {e}")

    def view_files(self):
        self.file_listbox.delete(0, tk.END)
        files = os.listdir(STORAGE_DIR)
        for f in files:
            self.file_listbox.insert(tk.END, f)
        if not files:
            self.log("Storage folder is empty.")

    def sync_now(self):
        self.log("🔁 Starting sync with nodes...")
        threading.Thread(target=self.sync_files).start()

    def sync_files(self):
        local_files = set(os.listdir(STORAGE_DIR))
        for node in NODES:
            try:
                r = requests.get(f"http://{node}/files", timeout=5)
                if r.status_code == 200:
                    their_files = set(json.loads(r.text))
                    missing = local_files - their_files
                    for file in missing:
                        with open(os.path.join(STORAGE_DIR, file), 'rb') as f:
                            headers = {'Filename': file}
                            requests.post(f"http://{node}/upload", data=f.read(), headers=headers, timeout=10)
                            self.log(f"✔ Sent '{file}' to {node}")
                else:
                    self.log(f"⚠️ Failed to sync with {node} (code {r.status_code})")
            except Exception as e:
                self.log(f"⚠️ Node {node} not reachable: {e}")
        self.log("✅ Sync completed.")

if __name__ == '__main__':
    root = tk.Tk()
    app = BackupGUI(root)
    root.mainloop()

