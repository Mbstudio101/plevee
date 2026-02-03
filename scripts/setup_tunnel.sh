#!/bin/bash

# Cloudflare Tunnel Setup Script for Plevee
# This script sets up a permanent public URL for your local Plevee backend

echo "🚀 Plevee - Cloudflare Tunnel Setup"
echo "===================================="
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "📦 Installing cloudflared..."
    brew install cloudflared
fi

# Login to Cloudflare
echo ""
echo "🔐 Please login to Cloudflare (browser will open)..."
cloudflared tunnel login

# Create tunnel
echo ""
echo "🔧 Creating tunnel 'plevee'..."
cloudflared tunnel create plevee

# Get tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep plevee | awk '{print $1}')

# Create config file
echo ""
echo "📝 Creating tunnel configuration..."
mkdir -p ~/.cloudflared

cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_ID
credentials-file: ~/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: plevee.your-domain.com
    service: http://localhost:8000
  - service: http_status:404
EOF

echo ""
echo "✅ Tunnel created successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update hostname in ~/.cloudflared/config.yml"
echo "2. Run: cloudflared tunnel route dns plevee plevee.your-domain.com"
echo "3. Run: cloudflared tunnel run plevee"
echo ""
echo "Or use quick mode (no domain needed):"
echo "cloudflared tunnel --url http://localhost:8000"
