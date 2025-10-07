#!/bin/bash

# Quick Network Setup Helper Script
# Helps you configure the backup system for multi-device setup

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         🌐 Backup System - Network Setup Helper  🌐            ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Detect local IP
echo "📡 Detecting your local IP address..."
if command -v hostname &> /dev/null; then
    LOCAL_IP=$(hostname -I | awk '{print $1}')
elif command -v ip &> /dev/null; then
    LOCAL_IP=$(ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 | head -1)
else
    LOCAL_IP="Unknown"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  THIS DEVICE INFORMATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Hostname: $(hostname)"
echo "  Local IP: $LOCAL_IP"
echo "  Port:     8000 (node server)"
echo "  Address:  $LOCAL_IP:8000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if config exists
if [ -f "config.json" ]; then
    echo "📋 Current configuration:"
    echo ""
    cat config.json
    echo ""
    read -p "Do you want to reconfigure? (y/n): " reconfigure
    if [ "$reconfigure" != "y" ]; then
        echo "Keeping existing configuration."
        exit 0
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  NETWORK SETUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "How many devices will be in your backup network?"
read -p "Number of devices (including this one): " num_devices

if ! [[ "$num_devices" =~ ^[0-9]+$ ]] || [ "$num_devices" -lt 1 ]; then
    echo "Invalid number. Exiting."
    exit 1
fi

echo ""
echo "Enter the IP address for each device (format: 192.168.1.X)"
echo "Press ENTER to use this device's IP ($LOCAL_IP) when prompted"
echo ""

nodes=()
for ((i=1; i<=num_devices; i++)); do
    read -p "Device $i IP address: " ip
    
    # Use local IP if empty
    if [ -z "$ip" ]; then
        ip="$LOCAL_IP"
    fi
    
    # Add port if not included
    if [[ ! "$ip" =~ :[0-9]+$ ]]; then
        ip="$ip:8000"
    fi
    
    nodes+=("$ip")
    echo "  ✓ Added: $ip"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  GENERATING CONFIG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Generate config.json
echo "{" > config.json
echo "  \"nodes\": [" >> config.json

for ((i=0; i<${#nodes[@]}; i++)); do
    if [ $i -eq $((${#nodes[@]}-1)) ]; then
        echo "    \"${nodes[$i]}\"" >> config.json
    else
        echo "    \"${nodes[$i]}\"," >> config.json
    fi
done

echo "  ]" >> config.json
echo "}" >> config.json

echo "✅ Configuration saved to config.json"
echo ""
cat config.json
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  FIREWALL SETUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To allow connections, you need to open port 8000 in your firewall."
echo ""

# Detect firewall
if command -v ufw &> /dev/null; then
    read -p "Configure UFW firewall now? (y/n): " config_fw
    if [ "$config_fw" = "y" ]; then
        echo "Opening port 8000..."
        sudo ufw allow 8000/tcp
        sudo ufw allow 5000/tcp
        echo "✓ Firewall configured"
    fi
elif command -v firewall-cmd &> /dev/null; then
    read -p "Configure firewalld now? (y/n): " config_fw
    if [ "$config_fw" = "y" ]; then
        echo "Opening port 8000..."
        sudo firewall-cmd --permanent --add-port=8000/tcp
        sudo firewall-cmd --permanent --add-port=5000/tcp
        sudo firewall-cmd --reload
        echo "✓ Firewall configured"
    fi
else
    echo "⚠️  Firewall tool not detected."
    echo "    Manually allow port 8000 in your firewall settings."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  NEXT STEPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Configuration complete!"
echo ""
echo "On THIS device:"
echo "  1. Start the node server:"
echo "     source venv/bin/activate"
echo "     python node_v2.py"
echo ""
echo "On OTHER devices:"
echo "  1. Copy this entire project folder"
echo "  2. Copy the config.json file (same config for all devices)"
echo "  3. Install dependencies:"
echo "     python3 -m venv venv"
echo "     source venv/bin/activate"
echo "     pip install -r requirements.txt"
echo "  4. Start node server:"
echo "     python node_v2.py"
echo ""
echo "Optional:"
echo "  - Run GUI on any device: python gui_v2.py"
echo "  - Run Web GUI: python web_gui.py (access at http://$LOCAL_IP:5000)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 For detailed setup instructions, see: NETWORK_SETUP.md"
echo ""
echo "Ready to start? Run: ./start.sh"
echo ""
