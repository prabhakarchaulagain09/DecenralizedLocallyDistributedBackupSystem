# DecentralizedLocallyDistributedBackupSystem

A lightweight **decentralized file backup system** that turns your own devices into **distributed storage nodes**. Upload, sync, and manage your backups locally — without relying on third-party cloud services.

---

## Features

- Daily or manual synchronization between devices
- Local file storage and backup
- Peer-to-peer architecture — no central server required
- Desktop GUI built with Tkinter
- Upload, delete, and sync files with ease
- Fully offline & customizable (encryption, chunking, etc. optional)

---

## Project Structure

```
DecentralizedLocallyDistributedBackupSystem/
│
├── node.py # Node server (runs on all participating devices)
├── gui.py # GUI client for upload/sync/delete
├── config.json # List of IPs of other nodes/devices
├── storage/ # Local backup storage folder (auto-created)
└── README.md # This file
```

---

## How It Works

Each of your devices becomes a **node** that:
- Hosts a small HTTP server (`node.py`)
- Shares files from its `storage/` folder
- Automatically syncs missing files once per day — or when you click "Sync Now"

The GUI (`gui.py`) lets you:
- Upload files to your local storage folder
- Delete files locally
- Manually trigger sync to other online devices
- View all stored files
- Track operations in a scrollable log panel

---

## 🛠️ Setup Instructions

### Step 1: On All Devices (Nodes)
These steps must be done on every participating device.

1. Install Python 3
2. Clone/download this repository
3. Create or update `config.json`:
```json
{
  "nodes": [
    "192.168.1.10:8000",
    "192.168.1.11:8000",
    "192.168.1.12:8000"
  ]
}
```

Replace the IPs with the actual local IPs of your devices.

4. Start the node server:
   ```bash
   python3 node.py
   ```
Leave this running in a terminal or background process (use tmux, nohup, or a service).

### 🖥️ Step 2: On Your Primary Device (GUI Controller)
This can be one of the nodes or a separate one.

  1. Make sure requests is installed:
     
```bash
pip install requests
```

  2. Run the GUI:

```bash
python3 gui.py
```

---

## GUI Features

  Add File: Upload a file from your device to the local storage folder

  Delete File: Remove a file from local storage

  Sync Now: Send missing files to all online nodes

  Refresh Files: View latest file list

  Activity Log: Shows all operations and sync status
  
---

## Example Use Case

  Laptop, desktop, and Raspberry Pi all run node.py

  Your main laptop runs the GUI

  You upload files from your laptop

  All devices sync automatically when they're online at the same time

  No cloud, no internet required — just your own local network

  ---

## Optional Future Enhancements

  Encryption for secure file storage

  File chunking for large files

  Version control and deduplication

  Web-based GUI

  CLI utility for automation/scripts

---

## 🙌 Author

Prabhakar Chaulagain 
```
Built with ❤️ to take back control of your personal data.
```

