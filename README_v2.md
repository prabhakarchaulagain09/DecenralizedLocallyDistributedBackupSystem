# DecentralizedLocallyDistributedBackupSystem - v2.0

A lightweight **decentralized file backup system** that turns your own devices into **distributed storage nodes**. Upload, sync, and manage your backups locally — without relying on third-party cloud services.

## 🎉 What's New in v2.0

### Major Upgrades:
- ✨ **Modern Desktop GUI** with dark theme and professional styling
- 🌐 **Web-based GUI** for browser access (responsive design)
- 🔒 **Enhanced Security** with file hashing and integrity checks
- 📊 **Better Metadata** tracking (file size, hash, timestamps)
- 🔄 **Bidirectional Sync** (push AND pull files)
- 📝 **Comprehensive Logging** system
- ⚡ **Performance Improvements** and better error handling
- 🎨 **Beautiful UI** with progress indicators and real-time status
- 🔧 **Settings Panel** for easy node configuration
- 📈 **Statistics Dashboard** showing system health

---

## Features

### Core Features
- ✅ Daily or manual synchronization between devices
- ✅ Local file storage and backup
- ✅ Peer-to-peer architecture — no central server required
- ✅ Multiple GUI options (Desktop Tkinter, Web Browser)
- ✅ Upload, delete, and sync files with ease
- ✅ Fully offline & customizable

### v2.0 Enhancements
- ✅ File integrity verification with MD5 hashing
- ✅ Automatic file metadata tracking
- ✅ Real-time node status monitoring
- ✅ Bidirectional file synchronization
- ✅ Comprehensive activity logging
- ✅ Professional error handling
- ✅ Self-detection (prevents syncing with self)
- ✅ Health check endpoints
- ✅ Modern, responsive UI design
- ✅ Virtual environment support

---

## 📁 Project Structure

```
DecentralizedLocallyDistributedBackupSystem/
│
├── node.py              # Original node server
├── node_v2.py          # ⭐ Enhanced node server (recommended)
├── gui.py              # Original GUI client
├── gui_v2.py           # ⭐ Modern desktop GUI (recommended)
├── web_gui.py          # ⭐ Web-based GUI (NEW!)
├── templates/
│   └── index.html      # Web GUI frontend
├── config.json         # Node configuration
├── requirements.txt    # Python dependencies
├── start.sh            # Quick start script
├── storage/            # Local backup storage (auto-created)
├── metadata.json       # File metadata (auto-created)
├── node.log            # Server logs (auto-created)
└── README.md           # This file
```

---

## 🚀 Quick Start

### Method 1: Using the Start Script (Easiest)

```bash
./start.sh
```

The script will:
1. Create a virtual environment
2. Install all dependencies
3. Give you options to run different components

### Method 2: Manual Setup

#### Step 1: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

#### Step 2: Configure Nodes

Edit `config.json` or use the Settings panel in the GUI:

```json
{
  "nodes": [
    "192.168.1.10:8000",
    "192.168.1.11:8000",
    "192.168.1.12:8000"
  ]
}
```

Replace with your actual device IPs.

#### Step 3: Run the System

**Option A: Enhanced Desktop GUI (Recommended)**
```bash
python gui_v2.py
```

**Option B: Web-based GUI**
```bash
python web_gui.py
# Open http://localhost:5000 in your browser
```

**Option C: Node Server (on all devices)**
```bash
python node_v2.py
```

---

## 🖥️ GUI Comparison

### Enhanced Desktop GUI (`gui_v2.py`)
- ✅ Modern dark theme
- ✅ Real-time file tree view
- ✅ Activity log with color-coded messages
- ✅ Node status indicator
- ✅ File size and hash display
- ✅ Settings panel
- ✅ Multi-file upload support
- ✅ Professional styling

### Web-based GUI (`web_gui.py`)
- ✅ Access from any browser
- ✅ Responsive design (mobile-friendly)
- ✅ Beautiful gradient theme
- ✅ Real-time statistics
- ✅ Drag-and-drop file upload
- ✅ Modal settings dialog
- ✅ Console-style activity log
- ✅ No Tkinter dependency required

### Original GUI (`gui.py`)
- ✅ Simple and lightweight
- ✅ Classic Tkinter interface
- ✅ Basic functionality

---

## 🔧 Advanced Usage

### Running as a Background Service

#### Using tmux:
```bash
tmux new -s backup-node
source venv/bin/activate
python node_v2.py
# Press Ctrl+B then D to detach
```

#### Using systemd (Linux):
Create `/etc/systemd/system/backup-node.service`:

```ini
[Unit]
Description=Decentralized Backup Node
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/DecenralizedLocallyDistributedBackupSystem
ExecStart=/path/to/DecenralizedLocallyDistributedBackupSystem/venv/bin/python node_v2.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable backup-node
sudo systemctl start backup-node
```

### API Endpoints (Node Server)

- `GET /files` - List all files with metadata
- `GET /download?filename=X` - Download a file
- `POST /upload` - Upload a file
- `POST /delete` - Delete a file
- `GET /health` - Health check

### API Endpoints (Web GUI)

- `GET /api/files` - Get file list
- `POST /api/upload` - Upload file
- `DELETE /api/delete/<filename>` - Delete file
- `GET /api/download/<filename>` - Download file
- `POST /api/sync` - Trigger sync
- `GET /api/stats` - Get statistics
- `GET /api/nodes` - Get node list
- `POST /api/nodes` - Update nodes

---

## 📊 Feature Comparison

| Feature | Original | v2.0 Enhanced |
|---------|----------|---------------|
| Basic file sync | ✅ | ✅ |
| Desktop GUI | ✅ | ✅ (Better) |
| Web GUI | ❌ | ✅ |
| File hashing | ❌ | ✅ |
| Metadata tracking | ❌ | ✅ |
| Bidirectional sync | ❌ | ✅ |
| Logging system | Basic | Advanced |
| Error handling | Basic | Comprehensive |
| UI/UX | Basic | Modern |
| Self-detection | ❌ | ✅ |
| Health checks | ❌ | ✅ |
| Settings panel | ❌ | ✅ |
| File size display | ❌ | ✅ |
| Node status | ❌ | ✅ |
| Virtual env support | ❌ | ✅ |

---

## 🎯 Use Cases

### Personal Backup Network
- Laptop, desktop, and Raspberry Pi all run `node_v2.py`
- Main laptop runs the GUI
- Upload files from anywhere
- All devices sync automatically

### Home Media Server
- Distribute media across multiple devices
- Access from any device on the network
- Automatic redundancy

### Office Document Sharing
- Share files across team devices
- No cloud subscription needed
- Complete data privacy

### Development Project Sync
- Keep code in sync across workstations
- Local network speeds
- Version tracking with metadata

---

## 🛠️ Troubleshooting

### GUI won't start
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Check Tkinter is installed
python -m tkinter

# If missing, install:
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo pacman -S tk  # Arch Linux
```

### Nodes can't connect
- Check firewall settings (allow port 8000)
- Verify IP addresses in `config.json`
- Ensure nodes are on the same network
- Check `node.log` for errors

### Files not syncing
- Verify node servers are running
- Check network connectivity
- Review activity log in GUI
- Examine `node.log` files

### Web GUI not accessible
```bash
# Check if Flask is running
ps aux | grep web_gui.py

# Check port availability
netstat -tuln | grep 5000

# Try different port
python web_gui.py --port 5001
```

---

## 🔮 Future Enhancements

### Planned Features
- 🔐 End-to-end encryption
- 📦 File chunking for large files
- 📜 Version control and file history
- 🔄 Differential sync (only changed parts)
- 📱 Mobile app (iOS/Android)
- 🐳 Docker containerization
- 🔌 Plugin system
- 👥 Multi-user support with permissions
- 🗜️ File compression
- 🔍 Full-text search
- 📊 Advanced analytics dashboard
- 🌍 WAN support with NAT traversal
- ⚡ WebSocket real-time updates

---

## 📚 Technical Details

### Dependencies
- **requests** - HTTP client for node communication
- **flask** - Web framework for web GUI
- **flask-cors** - CORS support for web API

### Architecture
- **Peer-to-peer design** - No central server
- **HTTP-based communication** - Simple REST API
- **Push/Pull sync model** - Bidirectional file transfer
- **Metadata-driven** - Track file state with hashes
- **Event-driven logging** - Comprehensive activity tracking

### Security Considerations
- Files transmitted unencrypted (use VPN for sensitive data)
- No authentication (trust-based network)
- Local network only (no internet exposure recommended)
- File path sanitization prevents directory traversal
- Future: Implement TLS and authentication

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Encryption implementation
- Better conflict resolution
- Performance optimization
- UI/UX enhancements
- Documentation
- Testing suite

---

## 📄 License

Apache License 2.0 - See LICENSE file for details.

---

## 🙌 Author

**Prabhakar Chaulagain**

```
Built with ❤️ to take back control of your personal data.
v2.0 - Now with 100% more style! 🎨
```

---

## 🎓 Learning Resources

This project demonstrates:
- Python HTTP server implementation
- Tkinter GUI development
- Flask web application development
- RESTful API design
- Peer-to-peer networking
- File system operations
- Threading and async operations
- Modern UI/UX principles

---

## 💡 Tips & Best Practices

1. **Always run node servers first** before using GUI
2. **Use static IPs** or hostnames for reliable connections
3. **Regular backups** - This is a backup system, but back it up too!
4. **Monitor logs** - Check `node.log` for issues
5. **Test on small files** first before large transfers
6. **Keep nodes updated** - Use same version on all devices
7. **Network health** - Ensure good connectivity between nodes
8. **Storage space** - Monitor available disk space

---

## 🔗 Quick Links

- **Original Version**: Use `node.py` and `gui.py`
- **Enhanced Version**: Use `node_v2.py` and `gui_v2.py`
- **Web Version**: Use `web_gui.py`
- **Quick Start**: Run `./start.sh`

---

**Enjoy your decentralized backup system! 🚀**
