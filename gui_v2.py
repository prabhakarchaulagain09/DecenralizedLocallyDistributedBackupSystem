import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import threading
from datetime import datetime
import hashlib

STORAGE_DIR = 'storage'
CONFIG_FILE = 'config.json'

os.makedirs(STORAGE_DIR, exist_ok=True)

# Load configuration
def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {"nodes": []}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    with open(CONFIG_FILE) as f:
        return json.load(f)

config = load_config()
NODES = config.get('nodes', [])

class ModernBackupGUI:
    def __init__(self, master):
        self.master = master
        master.title("🌐 Decentralized Backup System")
        master.geometry("900x700")
        
        # Color scheme
        self.bg_dark = "#1e1e1e"
        self.bg_medium = "#2d2d2d"
        self.bg_light = "#3c3c3c"
        self.accent = "#007acc"
        self.accent_hover = "#005a9e"
        self.text_color = "#ffffff"
        self.success = "#4ec9b0"
        self.warning = "#ce9178"
        self.error = "#f48771"
        
        # Apply dark theme
        master.configure(bg=self.bg_dark)
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', 
                       background=self.bg_dark, 
                       foreground=self.text_color, 
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Header.TLabel',
                       background=self.bg_dark,
                       foreground=self.text_color,
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('TFrame', background=self.bg_dark)
        
        style.configure('Card.TFrame', background=self.bg_medium, relief='raised')
        
        # Button styles
        style.configure('Accent.TButton',
                       background=self.accent,
                       foreground=self.text_color,
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9))
        
        style.map('Accent.TButton',
                 background=[('active', self.accent_hover)])
        
        # Create main layout
        self.create_widgets()
        
        # Initial load
        self.log("🚀 Application started", "success")
        self.refresh_files()
        self.update_node_status()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.master, style='TFrame')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = ttk.Label(header_frame, 
                               text="🌐 Decentralized Backup System",
                               style='Title.TLabel')
        title_label.pack(side='left')
        
        # Node status indicator
        self.status_label = tk.Label(header_frame,
                                     text="● Online",
                                     bg=self.bg_dark,
                                     fg=self.success,
                                     font=('Segoe UI', 10))
        self.status_label.pack(side='right')
        
        # Action buttons frame
        action_frame = ttk.Frame(self.master, style='TFrame')
        action_frame.pack(fill='x', padx=20, pady=10)
        
        # Buttons
        btn_config = [
            ("➕ Add Files", self.upload_file, self.accent),
            ("🗑️ Delete", self.delete_file, self.error),
            ("🔄 Sync Now", self.sync_now, self.success),
            ("↻ Refresh", self.refresh_files, self.bg_light),
            ("⚙️ Settings", self.show_settings, self.bg_light)
        ]
        
        for i, (text, command, color) in enumerate(btn_config):
            btn = tk.Button(action_frame,
                           text=text,
                           command=command,
                           bg=color,
                           fg=self.text_color,
                           font=('Segoe UI', 9, 'bold'),
                           relief='flat',
                           padx=15,
                           pady=8,
                           cursor='hand2',
                           activebackground=self.accent_hover)
            btn.pack(side='left', padx=5)
            
            # Add hover effect
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.configure(bg=self.lighten_color(c)))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.configure(bg=c))
        
        # Files section
        files_container = ttk.Frame(self.master, style='Card.TFrame')
        files_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Files header
        files_header = ttk.Frame(files_container, style='Card.TFrame')
        files_header.pack(fill='x', padx=10, pady=(10, 5))
        
        ttk.Label(files_header, 
                 text="📁 Files in Storage",
                 style='Header.TLabel').pack(side='left')
        
        self.file_count_label = tk.Label(files_header,
                                         text="0 files",
                                         bg=self.bg_medium,
                                         fg=self.warning,
                                         font=('Segoe UI', 9))
        self.file_count_label.pack(side='right', padx=10)
        
        # Files treeview
        tree_frame = ttk.Frame(files_container, style='Card.TFrame')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        self.file_tree = ttk.Treeview(tree_frame,
                                      columns=('Name', 'Size', 'Modified', 'Hash'),
                                      show='headings',
                                      yscrollcommand=vsb.set,
                                      xscrollcommand=hsb.set,
                                      selectmode='browse')
        
        vsb.config(command=self.file_tree.yview)
        hsb.config(command=self.file_tree.xview)
        
        # Column configuration
        self.file_tree.heading('Name', text='📄 File Name')
        self.file_tree.heading('Size', text='📊 Size')
        self.file_tree.heading('Modified', text='🕒 Modified')
        self.file_tree.heading('Hash', text='🔒 Hash')
        
        self.file_tree.column('Name', width=300)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Modified', width=150)
        self.file_tree.column('Hash', width=200)
        
        # Pack treeview and scrollbars
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Style treeview
        style = ttk.Style()
        style.configure('Treeview',
                       background=self.bg_light,
                       foreground=self.text_color,
                       fieldbackground=self.bg_light,
                       borderwidth=0)
        style.configure('Treeview.Heading',
                       background=self.bg_medium,
                       foreground=self.text_color,
                       borderwidth=0)
        style.map('Treeview',
                 background=[('selected', self.accent)])
        
        # Activity log
        log_container = ttk.Frame(self.master, style='Card.TFrame')
        log_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        log_header = ttk.Frame(log_container, style='Card.TFrame')
        log_header.pack(fill='x', padx=10, pady=(10, 5))
        
        ttk.Label(log_header,
                 text="📋 Activity Log",
                 style='Header.TLabel').pack(side='left')
        
        clear_btn = tk.Button(log_header,
                             text="Clear",
                             command=self.clear_log,
                             bg=self.bg_light,
                             fg=self.text_color,
                             font=('Segoe UI', 8),
                             relief='flat',
                             padx=10,
                             pady=3,
                             cursor='hand2')
        clear_btn.pack(side='right')
        
        # Log text area
        log_frame = ttk.Frame(log_container, style='Card.TFrame')
        log_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                  height=8,
                                                  bg=self.bg_light,
                                                  fg=self.text_color,
                                                  font=('Consolas', 9),
                                                  relief='flat',
                                                  insertbackground=self.text_color)
        self.log_text.pack(fill='both', expand=True)
        
        # Configure log tags
        self.log_text.tag_config('success', foreground=self.success)
        self.log_text.tag_config('error', foreground=self.error)
        self.log_text.tag_config('warning', foreground=self.warning)
        self.log_text.tag_config('info', foreground='#9cdcfe')
    
    def lighten_color(self, color):
        """Lighten a hex color"""
        if color.startswith('#'):
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            r = min(255, r + 20)
            g = min(255, g + 20)
            b = min(255, b + 20)
            return f'#{r:02x}{g:02x}{b:02x}'
        return color
    
    def log(self, message, tag='info'):
        """Add message to log with timestamp and styling"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] ", 'info')
        self.log_text.insert(tk.END, f"{message}\n", tag)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        self.log("Log cleared", "info")
    
    def format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def refresh_files(self):
        """Refresh file list"""
        self.file_tree.delete(*self.file_tree.get_children())
        
        try:
            files = os.listdir(STORAGE_DIR)
            file_count = 0
            
            for filename in files:
                filepath = os.path.join(STORAGE_DIR, filename)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    # Calculate hash for first 1KB (for speed)
                    with open(filepath, 'rb') as f:
                        file_hash = hashlib.md5(f.read(1024)).hexdigest()[:8]
                    
                    self.file_tree.insert('', 'end', values=(
                        filename,
                        self.format_size(size),
                        mtime.strftime('%Y-%m-%d %H:%M'),
                        file_hash + '...'
                    ))
                    file_count += 1
            
            self.file_count_label.config(text=f"{file_count} file{'s' if file_count != 1 else ''}")
            
            if file_count == 0:
                self.log("Storage folder is empty", "warning")
        except Exception as e:
            self.log(f"Error refreshing files: {e}", "error")
    
    def upload_file(self):
        """Upload file(s) to storage"""
        paths = filedialog.askopenfilenames(title="Select files to add")
        if not paths:
            return
        
        for path in paths:
            try:
                filename = os.path.basename(path)
                dest_path = os.path.join(STORAGE_DIR, filename)
                
                with open(path, 'rb') as src, open(dest_path, 'wb') as dst:
                    dst.write(src.read())
                
                self.log(f"✓ Added '{filename}' to storage", "success")
            except Exception as e:
                self.log(f"✗ Failed to add '{filename}': {e}", "error")
        
        self.refresh_files()
    
    def delete_file(self):
        """Delete selected file"""
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a file to delete")
            return
        
        item = self.file_tree.item(selection[0])
        filename = item['values'][0]
        
        confirm = messagebox.askyesno("Confirm Delete",
                                     f"Delete '{filename}'?\n\nThis will remove it from local storage.")
        if not confirm:
            return
        
        try:
            filepath = os.path.join(STORAGE_DIR, filename)
            os.remove(filepath)
            self.log(f"✓ Deleted '{filename}'", "success")
            self.refresh_files()
        except Exception as e:
            self.log(f"✗ Failed to delete '{filename}': {e}", "error")
    
    def sync_now(self):
        """Trigger manual sync"""
        self.log("🔄 Starting synchronization...", "info")
        threading.Thread(target=self.sync_files, daemon=True).start()
    
    def sync_files(self):
        """Perform sync with all nodes"""
        if not NODES:
            self.log("⚠ No nodes configured. Add nodes in settings.", "warning")
            return
        
        try:
            local_files = set(os.listdir(STORAGE_DIR))
            synced_nodes = 0
            
            for node in NODES:
                try:
                    # Get their file list
                    r = requests.get(f"http://{node}/files", timeout=5)
                    if r.status_code != 200:
                        self.log(f"⚠ Could not reach {node}", "warning")
                        continue
                    
                    remote_files_data = r.json()
                    remote_files = {f['name'] if isinstance(f, dict) else f 
                                  for f in remote_files_data}
                    
                    # Send missing files
                    missing = local_files - remote_files
                    for filename in missing:
                        filepath = os.path.join(STORAGE_DIR, filename)
                        try:
                            with open(filepath, 'rb') as f:
                                headers = {'Filename': filename}
                                resp = requests.post(
                                    f"http://{node}/upload",
                                    data=f.read(),
                                    headers=headers,
                                    timeout=30
                                )
                                if resp.status_code == 200:
                                    self.log(f"✓ Sent '{filename}' → {node}", "success")
                        except Exception as e:
                            self.log(f"✗ Failed to send '{filename}' to {node}: {e}", "error")
                    
                    if not missing:
                        self.log(f"✓ {node} is up to date", "success")
                    
                    synced_nodes += 1
                    
                except requests.exceptions.Timeout:
                    self.log(f"⚠ Timeout connecting to {node}", "warning")
                except requests.exceptions.ConnectionError:
                    self.log(f"⚠ Cannot connect to {node}", "warning")
                except Exception as e:
                    self.log(f"✗ Error syncing with {node}: {e}", "error")
            
            if synced_nodes > 0:
                self.log(f"✅ Sync complete ({synced_nodes}/{len(NODES)} nodes)", "success")
            else:
                self.log("⚠ No nodes were reachable", "warning")
                
        except Exception as e:
            self.log(f"✗ Sync failed: {e}", "error")
    
    def update_node_status(self):
        """Update node connection status"""
        def check_status():
            online = 0
            for node in NODES:
                try:
                    r = requests.get(f"http://{node}/health", timeout=2)
                    if r.status_code == 200:
                        online += 1
                except:
                    pass
            
            status_text = f"● {online}/{len(NODES)} nodes online" if NODES else "● No nodes configured"
            color = self.success if online > 0 else self.warning
            self.status_label.config(text=status_text, fg=color)
        
        threading.Thread(target=check_status, daemon=True).start()
        # Update every 30 seconds
        self.master.after(30000, self.update_node_status)
    
    def show_settings(self):
        """Show settings dialog"""
        settings_win = tk.Toplevel(self.master)
        settings_win.title("⚙️ Settings")
        settings_win.geometry("500x400")
        settings_win.configure(bg=self.bg_dark)
        
        # Title
        title = tk.Label(settings_win,
                        text="⚙️ Configuration",
                        bg=self.bg_dark,
                        fg=self.text_color,
                        font=('Segoe UI', 14, 'bold'))
        title.pack(pady=20)
        
        # Nodes section
        nodes_label = tk.Label(settings_win,
                              text="Network Nodes (IP:PORT)",
                              bg=self.bg_dark,
                              fg=self.text_color,
                              font=('Segoe UI', 10))
        nodes_label.pack(pady=(10, 5))
        
        nodes_text = scrolledtext.ScrolledText(settings_win,
                                              height=10,
                                              bg=self.bg_light,
                                              fg=self.text_color,
                                              font=('Consolas', 10),
                                              relief='flat')
        nodes_text.pack(padx=20, pady=10, fill='both', expand=True)
        
        # Load current nodes
        nodes_text.insert('1.0', '\n'.join(NODES))
        
        # Save button
        def save_settings():
            global NODES
            content = nodes_text.get('1.0', 'end-1c')
            new_nodes = [line.strip() for line in content.split('\n') if line.strip()]
            
            config['nodes'] = new_nodes
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            
            NODES = new_nodes
            self.log(f"✓ Settings saved ({len(NODES)} nodes configured)", "success")
            self.update_node_status()
            settings_win.destroy()
        
        save_btn = tk.Button(settings_win,
                            text="💾 Save Settings",
                            command=save_settings,
                            bg=self.accent,
                            fg=self.text_color,
                            font=('Segoe UI', 10, 'bold'),
                            relief='flat',
                            padx=20,
                            pady=10,
                            cursor='hand2')
        save_btn.pack(pady=10)

if __name__ == '__main__':
    root = tk.Tk()
    app = ModernBackupGUI(root)
    root.mainloop()
