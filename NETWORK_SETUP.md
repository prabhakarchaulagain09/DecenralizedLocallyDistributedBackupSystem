# 🌐 Network Setup Guide - Connecting Multiple Devices

## Overview
This guide shows you how to connect multiple devices (laptop, desktop, Raspberry Pi, etc.) to create your decentralized backup network.

---

## 📋 Prerequisites

Before connecting devices, ensure:
- ✅ All devices are on the **same local network** (same WiFi/router)
- ✅ Python 3 is installed on all devices
- ✅ Devices can communicate with each other
- ✅ Firewall allows port 8000 (and 5000 for web GUI)

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Find Your Device IP Addresses

On each device, run one of these commands:

**Linux/Mac:**
```bash
hostname -I | awk '{print $1}'
# or
ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1
```

**Windows:**
```cmd
ipconfig | findstr IPv4
```

**Example IPs you might get:**
- Laptop: `192.168.1.10`
- Desktop: `192.168.1.11`
- Raspberry Pi: `192.168.1.12`

### Step 2: Install & Configure on Each Device

**On EVERY device:**

```bash
# 1. Clone or copy the project
git clone <your-repo-url>
cd DecenralizedLocallyDistributedBackupSystem

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Edit config.json with ALL device IPs
nano config.json  # or use any text editor
```

**Example `config.json`** (same on all devices):
```json
{
  "nodes": [
    "192.168.1.10:8000",
    "192.168.1.11:8000",
    "192.168.1.12:8000"
  ]
}
```

⚠️ **Important:** Include ALL device IPs in the config, including the device itself (the system will automatically skip syncing with itself).

### Step 3: Start Node Server on Each Device

**On EVERY device, run:**

```bash
source venv/bin/activate
python node_v2.py
```

You should see:
```
INFO - Starting node at 192.168.1.10:8000
INFO - Connected nodes: ['192.168.1.11:8000', '192.168.1.12:8000']
INFO - 🚀 Node server running at 192.168.1.10:8000 with bidirectional sync
```

✅ **Done!** Your network is now connected and syncing automatically every 24 hours.

---

## 🖥️ Using the GUI (Optional)

You can run the GUI on **one or more devices** to manage files:

### Desktop GUI

```bash
source venv/bin/activate
python gui_v2.py
```

### Web GUI

```bash
source venv/bin/activate
python web_gui.py
```

Then open `http://localhost:5000` (or `http://<device-ip>:5000` from other devices)

---

## 📝 Detailed Step-by-Step Example

### Example: Setting up 3 Devices

#### **Device 1: Laptop (192.168.1.10)**

```bash
# Terminal 1: Start node server
cd ~/DecenralizedLocallyDistributedBackupSystem
source venv/bin/activate
python node_v2.py

# Terminal 2 (optional): Start GUI
source venv/bin/activate
python gui_v2.py
```

#### **Device 2: Desktop (192.168.1.11)**

```bash
# Start node server
cd /path/to/DecenralizedLocallyDistributedBackupSystem
source venv/bin/activate
python node_v2.py
```

#### **Device 3: Raspberry Pi (192.168.1.12)**

```bash
# Start node server
cd /home/pi/DecenralizedLocallyDistributedBackupSystem
source venv/bin/activate
python node_v2.py
```

---

## 🔥 Firewall Configuration

### Linux (UFW)

```bash
# Allow incoming connections on port 8000
sudo ufw allow 8000/tcp

# If using web GUI, also allow port 5000
sudo ufw allow 5000/tcp

# Reload firewall
sudo ufw reload
```

### Linux (firewalld)

```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### Windows Firewall

```powershell
# Allow port 8000
New-NetFirewallRule -DisplayName "Backup Node" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# Allow port 5000 (for web GUI)
New-NetFirewallRule -DisplayName "Backup Web GUI" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

### macOS

```bash
# macOS usually allows local network traffic by default
# If needed, add rules in System Preferences > Security > Firewall
```

---

## ✅ Testing the Connection

### Test 1: Check if nodes are reachable

From any device:

```bash
# Ping other devices
ping 192.168.1.11
ping 192.168.1.12

# Test HTTP connection
curl http://192.168.1.11:8000/health
curl http://192.168.1.12:8000/health
```

Expected response:
```json
{"status":"healthy","storage_files":0,"nodes_configured":2,"local_address":"192.168.1.11:8000"}
```

### Test 2: Upload and Sync

1. **On Device 1:** Upload a file using the GUI
2. **On Device 1:** Click "🔄 Sync Now"
3. **On Device 2 & 3:** Check the `storage/` folder - the file should appear!

### Test 3: Check Logs

```bash
# View node logs
tail -f node.log
```

You should see sync activity like:
```
INFO - Starting sync cycle...
INFO - ✓ Pushed 'test.txt' to 192.168.1.11:8000
INFO - ✓ Pushed 'test.txt' to 192.168.1.12:8000
INFO - Sync cycle completed
```

---

## 🔧 Troubleshooting

### Problem: "Connection refused" errors

**Solution:**
```bash
# 1. Verify node server is running on target device
ps aux | grep node_v2.py

# 2. Check if port 8000 is listening
netstat -tuln | grep 8000
# or
ss -tuln | grep 8000

# 3. Test local connection first
curl http://localhost:8000/health

# 4. Test from another device
curl http://<target-ip>:8000/health
```

### Problem: "No route to host"

**Solution:**
```bash
# 1. Verify devices are on same network
ip route

# 2. Check if you can ping the device
ping <target-ip>

# 3. Verify IP address is correct
hostname -I
```

### Problem: Files not syncing

**Solution:**
```bash
# 1. Check config.json on all devices
cat config.json

# 2. Verify all nodes are listed
# 3. Check node logs for errors
tail -f node.log

# 4. Manually trigger sync from GUI
# Click "🔄 Sync Now" button

# 5. Check file metadata
cat metadata.json
```

### Problem: "Permission denied" on storage folder

**Solution:**
```bash
# Fix permissions
chmod 755 storage/
chmod 644 storage/*
```

---

## 🏃 Running Node Server in Background

### Using tmux (Recommended)

```bash
# Install tmux
sudo apt install tmux  # Ubuntu/Debian
sudo pacman -S tmux    # Arch

# Start a session
tmux new -s backup-node

# Inside tmux, start the node
cd ~/DecenralizedLocallyDistributedBackupSystem
source venv/bin/activate
python node_v2.py

# Detach from tmux: Press Ctrl+B, then D
# Reattach later: tmux attach -t backup-node
```

### Using systemd (Linux Service)

Create `/etc/systemd/system/backup-node.service`:

```ini
[Unit]
Description=Decentralized Backup Node
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/DecenralizedLocallyDistributedBackupSystem
ExecStart=/home/your-username/DecenralizedLocallyDistributedBackupSystem/venv/bin/python node_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable backup-node
sudo systemctl start backup-node

# Check status
sudo systemctl status backup-node

# View logs
sudo journalctl -u backup-node -f
```

### Using nohup (Simple)

```bash
cd ~/DecenralizedLocallyDistributedBackupSystem
source venv/bin/activate
nohup python node_v2.py > node_output.log 2>&1 &

# Check if running
ps aux | grep node_v2.py

# Stop it later
pkill -f node_v2.py
```

---

## 📊 Network Topology Examples

### Example 1: Home Network (3 devices)

```
Router (192.168.1.1)
├── Laptop (192.168.1.10) - Node + GUI
├── Desktop (192.168.1.11) - Node
└── Raspberry Pi (192.168.1.12) - Node
```

**config.json** (same on all):
```json
{
  "nodes": [
    "192.168.1.10:8000",
    "192.168.1.11:8000",
    "192.168.1.12:8000"
  ]
}
```

### Example 2: Office Network (5 devices)

```
Office Router (10.0.0.1)
├── Main Server (10.0.0.100) - Node + Web GUI
├── Workstation 1 (10.0.0.101) - Node
├── Workstation 2 (10.0.0.102) - Node
├── NAS (10.0.0.103) - Node
└── Laptop (10.0.0.104) - Node + Desktop GUI
```

**config.json**:
```json
{
  "nodes": [
    "10.0.0.100:8000",
    "10.0.0.101:8000",
    "10.0.0.102:8000",
    "10.0.0.103:8000",
    "10.0.0.104:8000"
  ]
}
```

---

## 🔒 Security Best Practices

1. **Use on trusted local networks only**
   - Don't expose to the internet
   - Use VPN if accessing remotely

2. **Set static IPs** (optional but recommended)
   ```bash
   # In your router's DHCP settings, reserve IPs for each device
   ```

3. **Regular backups of the backup system**
   ```bash
   # Backup your storage folder
   tar -czf backup-$(date +%Y%m%d).tar.gz storage/
   ```

4. **Monitor logs**
   ```bash
   # Check for unusual activity
   grep ERROR node.log
   grep WARNING node.log
   ```

---

## 📱 Accessing from Mobile Devices

While the web GUI is responsive, here's how to access from phones/tablets:

1. **Find your computer's IP** (e.g., 192.168.1.10)
2. **Start web GUI** on that computer:
   ```bash
   python web_gui.py
   ```
3. **On your phone/tablet:** Open browser and go to:
   ```
   http://192.168.1.10:5000
   ```

✅ You can now upload/download files from your mobile device!

---

## 🎯 Quick Reference

### Common Commands

```bash
# Find your IP
hostname -I | awk '{print $1}'

# Start node server
source venv/bin/activate && python node_v2.py

# Start desktop GUI
source venv/bin/activate && python gui_v2.py

# Start web GUI
source venv/bin/activate && python web_gui.py

# Check node health
curl http://localhost:8000/health

# View logs
tail -f node.log

# Test sync
curl http://<node-ip>:8000/files
```

### Port Reference

- **8000** - Node server (HTTP API)
- **5000** - Web GUI (Flask server)

### File Locations

- **Config:** `config.json`
- **Storage:** `storage/`
- **Metadata:** `metadata.json`
- **Logs:** `node.log`

---

## ✨ Tips for Best Experience

1. **Use static IPs** or reserve DHCP leases in your router
2. **Start nodes before GUI** - ensure backend is ready
3. **Keep configs synchronized** - same config.json on all devices
4. **Monitor storage space** - ensure adequate disk space
5. **Regular testing** - upload a file and verify it syncs
6. **Check logs periodically** - catch issues early
7. **Use systemd services** - for always-on nodes

---

## 🎉 Success Checklist

- [ ] All devices have Python 3 installed
- [ ] Project copied/cloned to all devices
- [ ] Virtual environment created on all devices
- [ ] Dependencies installed on all devices
- [ ] config.json configured with all IPs
- [ ] Firewall allows port 8000 (and 5000)
- [ ] Node servers running on all devices
- [ ] Can ping all devices from each other
- [ ] Health check returns success from all nodes
- [ ] Test file successfully synced to all devices

---

## 🆘 Need Help?

Check these files for more information:
- **README_v2.md** - Full documentation
- **UPGRADE_SUMMARY.md** - Technical details
- **SUCCESS.md** - Quick start guide

Or check the logs:
```bash
tail -f node.log  # Server logs
```

---

**Happy syncing! Your decentralized backup network is ready! 🚀**
