#!/bin/bash
# J.A.R.V.I.S System Setup Script
# Run with: sudo bash setup_system.sh

set -e

echo "🤖 Setting up J.A.R.V.I.S system dependencies..."

# Update package lists
echo "📦 Updating package lists..."
apt update

# Install required system packages
echo "📦 Installing system packages..."
apt install -y \
    ffmpeg \
    xdotool \
    xrandr \
    v4l-utils \
    curl \
    wget \
    git

# Grant camera access (will ask for password)
echo "📷 Setting up camera permissions..."
if [ -f /dev/video0 ]; then
    chmod 666 /dev/video0 2>/dev/null || true
    chmod 666 /dev/video1 2>/dev/null || true
fi

# Add user to video group (optional, may require logout)
if ! groups | grep -q video; then
    echo "👤 Adding user to video group..."
    echo "   Note: You may need to log out and back in for this to take effect"
fi

echo "✅ System dependencies installed!"
echo ""
echo "📝 Now install Python dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "🚀 Then start JARVIS:"
echo "   python agent.py"
