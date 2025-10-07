#!/bin/bash

# DecentralizedLocallyDistributedBackupSystem - Quick Start Script
# This script helps you get started quickly

echo "🌐 Decentralized Backup System - Quick Start"
echo "============================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Choose how to run the system:"
echo ""
echo "1️⃣  Enhanced Desktop GUI (Recommended)"
echo "   python gui_v2.py"
echo ""
echo "2️⃣  Web-based GUI (Modern, browser-based)"
echo "   python web_gui.py"
echo "   Then open: http://localhost:5000"
echo ""
echo "3️⃣  Node Server (Run on all devices)"
echo "   python node_v2.py"
echo ""
echo "4️⃣  Original Desktop GUI (Classic)"
echo "   python gui.py"
echo ""
echo "5️⃣  Original Node Server"
echo "   python node.py"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "🚀 Launching Enhanced Desktop GUI..."
        python gui_v2.py
        ;;
    2)
        echo "🌐 Launching Web GUI..."
        echo "Open http://localhost:5000 in your browser"
        python web_gui.py
        ;;
    3)
        echo "📡 Starting Node Server..."
        python node_v2.py
        ;;
    4)
        echo "🖥️  Launching Original GUI..."
        python gui.py
        ;;
    5)
        echo "📡 Starting Original Node..."
        python node.py
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        ;;
esac
