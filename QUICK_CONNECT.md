# Quick Start - Connecting Devices

## 🎯 3-Step Connection Guide

### Step 1️⃣: Find IP Addresses
```bash
# On each device, run:
hostname -I | awk '{print $1}'
```

**Example outputs:**
- Laptop: `192.168.1.10`
- Desktop: `192.168.1.11`
- Raspberry Pi: `192.168.1.12`

---

### Step 2️⃣: Configure Nodes

**Edit `config.json` on ALL devices (make it identical):**

```json
{
  "nodes": [
    "192.168.1.10:8000",
    "192.168.1.11:8000",
    "192.168.1.12:8000"
  ]
}
```

💡 **Tip:** Use the helper script:
```bash
./setup_network.sh
```

---

### Step 3️⃣: Start Node Servers

**On EVERY device:**

```bash
cd /path/to/DecenralizedLocallyDistributedBackupSystem
source venv/bin/activate
python node_v2.py
```

**Expected output:**
```
INFO - Starting node at 192.168.1.10:8000
INFO - Connected nodes: ['192.168.1.11:8000', '192.168.1.12:8000']
INFO - 🚀 Node server running at 192.168.1.10:8000 with bidirectional sync
```

---

## 🔥 Open Firewall Ports

### Linux (UFW)
```bash
sudo ufw allow 8000/tcp
sudo ufw allow 5000/tcp  # For web GUI
```

### Windows
```powershell
New-NetFirewallRule -DisplayName "Backup Node" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

---

## ✅ Test Connection

```bash
# From any device, test another:
curl http://192.168.1.11:8000/health

# Expected response:
# {"status":"healthy","storage_files":0,"nodes_configured":2,"local_address":"192.168.1.11:8000"}
```

---

## 📊 Visual Network Diagram

```
    ┌─────────────────────────────────────────┐
    │      Router (192.168.1.1)               │
    └──────────────┬──────────────────────────┘
                   │
         ┌─────────┼─────────┐
         │         │         │
         ▼         ▼         ▼
    ┌────────┐ ┌────────┐ ┌──────────┐
    │ Laptop │ │Desktop │ │ Rasp. Pi │
    │  .10   │ │  .11   │ │   .12    │
    └────────┘ └────────┘ └──────────┘
         │         │         │
         │    Port 8000     │
         └─────────┼─────────┘
                   │
              ┌────▼────┐
              │  Sync   │
              │Automatic│
              └─────────┘
```

---

## 🎮 Using the GUI

### Desktop GUI (any device)
```bash
source venv/bin/activate
python gui_v2.py
```

### Web GUI (access from anywhere)
```bash
# On one device:
source venv/bin/activate
python web_gui.py

# From any device/phone on network, open browser:
http://192.168.1.10:5000
```

---

## 🚨 Troubleshooting

### Can't connect to other nodes?

1. **Check if server is running:**
   ```bash
   ps aux | grep node_v2.py
   ```

2. **Check if port is open:**
   ```bash
   netstat -tuln | grep 8000
   ```

3. **Ping the device:**
   ```bash
   ping 192.168.1.11
   ```

4. **Check firewall:**
   ```bash
   sudo ufw status
   ```

5. **Check logs:**
   ```bash
   tail -f node.log
   ```

---

## 💡 Pro Tips

1. **Use static IPs** - Reserve IPs in router settings
2. **Run in background** - Use tmux or systemd (see NETWORK_SETUP.md)
3. **Same config everywhere** - Keep config.json identical on all devices
4. **Test before full deployment** - Try with 2 devices first
5. **Monitor logs** - Check `node.log` regularly

---

## 📚 Full Documentation

For detailed setup instructions, see:
- **NETWORK_SETUP.md** - Complete guide with all scenarios
- **README_v2.md** - Full feature documentation
- **SUCCESS.md** - Quick start guide

---

## 🆘 Quick Commands

```bash
# Find your IP
hostname -I | awk '{print $1}'

# Start node
source venv/bin/activate && python node_v2.py

# Test connection
curl http://<node-ip>:8000/health

# View logs
tail -f node.log

# Check running
ps aux | grep node_v2.py
```

---

**That's it! Your devices are now connected! 🎉**

Upload a file on one device and watch it appear on all others! ✨
