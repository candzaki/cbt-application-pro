#!/bin/bash
# ========================================================
# CBT Exam Pro v3 - HTTPS Starter with Fallback Tunnels
# Run: bash start_https.sh
# ========================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLOUDFLARED="/tmp/cloudflared"
PYTHON="$SCRIPT_DIR/.venv/bin/python"
PORT=8501

# --- Setup local logs ---
STREAMLIT_LOG="$SCRIPT_DIR/streamlit_cbt.log"
TUNNEL_LOG="$SCRIPT_DIR/tunnel_cbt.log"
rm -f "$STREAMLIT_LOG" "$TUNNEL_LOG"

# --- Check if cloudflared exists, download if not ---
if [ ! -f "$CLOUDFLARED" ]; then
    echo "⏬ Mendownload Cloudflare Tunnel..."
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ]; then
        BINARY="cloudflared-darwin-arm64.tgz"
    else
        BINARY="cloudflared-darwin-amd64.tgz"
    fi
    curl -L --progress-bar "https://github.com/cloudflare/cloudflared/releases/latest/download/$BINARY" -o /tmp/cloudflared.tgz
    tar -xzf /tmp/cloudflared.tgz -C /tmp/
    rm -f /tmp/cloudflared.tgz
    chmod +x "$CLOUDFLARED"
    echo "✅ Cloudflared siap!"
fi

# --- Remove Gatekeeper quarantine on macOS ---
if [ "$(uname)" = "Darwin" ]; then
    echo "🛡️  Clearing macOS quarantine attribute from cloudflared..."
    xattr -d com.apple.quarantine "$CLOUDFLARED" 2>/dev/null || true
fi

# --- Kill any existing instances ---
echo "🧹 Cleaning up existing server or tunnel processes..."
pkill -f "streamlit run.*$PORT" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null
pkill -f "ssh.*ssh.localhost.run" 2>/dev/null
pkill -f "ssh.*a.pinggy.io" 2>/dev/null
sleep 1

# Check if port 5001 is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT is already in use! Attempting to free it..."
    lsof -ti :$PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║    CBT Exam Pro v3 — HTTPS Launcher      ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# --- Start Streamlit in background ---
echo "🚀 Memulai Streamlit server di port $PORT..."
cd "$SCRIPT_DIR"
"$PYTHON" -m streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --browser.gatherUsageStats=false > "$STREAMLIT_LOG" 2>&1 &
STREAMLIT_PID=$!
echo "   Streamlit PID: $STREAMLIT_PID"
sleep 4

# Check if Streamlit successfully started
if ! ps -p $STREAMLIT_PID > /dev/null; then
    echo "❌ Streamlit gagal dijalankan. Cek log: $STREAMLIT_LOG"
    exit 1
fi

TUNNEL_PID=""
HTTPS_URL=""
PROVIDER=""

# --- Attempt 1: Cloudflare Tunnel ---
echo "🌐 Mencoba Cloudflare Tunnel (HTTPS) - Provider 1/3..."
"$CLOUDFLARED" tunnel --url http://localhost:$PORT --no-autoupdate > "$TUNNEL_LOG" 2>&1 &
TUNNEL_PID=$!

MAX_WAIT=12
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
    HTTPS_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$TUNNEL_LOG" 2>/dev/null | head -1)
    if [ -n "$HTTPS_URL" ]; then
        PROVIDER="Cloudflare"
        break
    fi
    sleep 1
    ELAPSED=$((ELAPSED + 1))
done

# --- Attempt 2: Localhost.run Fallback ---
if [ -z "$HTTPS_URL" ]; then
    echo "⚠️  Cloudflare Tunnel gagal/timeout. Mencoba Localhost.run - Provider 2/3..."
    kill $TUNNEL_PID 2>/dev/null
    rm -f "$TUNNEL_LOG"
    
    ssh -o StrictHostKeyChecking=no -R 80:localhost:$PORT ssh.localhost.run > "$TUNNEL_LOG" 2>&1 &
    TUNNEL_PID=$!
    
    MAX_WAIT=8
    ELAPSED=0
    while [ $ELAPSED -lt $MAX_WAIT ]; do
        HTTPS_URL=$(grep -o 'https://[a-z0-9-]*\.lhr\.life' "$TUNNEL_LOG" 2>/dev/null | head -1)
        if [ -n "$HTTPS_URL" ]; then
            PROVIDER="Localhost.run"
            break
        fi
        sleep 1
        ELAPSED=$((ELAPSED + 1))
    done
fi

# --- Attempt 3: Pinggy.io Fallback ---
if [ -z "$HTTPS_URL" ]; then
    echo "⚠️  Localhost.run gagal/timeout. Mencoba Pinggy.io - Provider 3/3..."
    kill $TUNNEL_PID 2>/dev/null
    rm -f "$TUNNEL_LOG"
    
    ssh -o StrictHostKeyChecking=no -p 443 -R 0:localhost:$PORT qr@a.pinggy.io > "$TUNNEL_LOG" 2>&1 &
    TUNNEL_PID=$!
    
    MAX_WAIT=18
    ELAPSED=0
    while [ $ELAPSED -lt $MAX_WAIT ]; do
        # Match both *.pinggy.link and *.run.pinggy-free.link
        HTTPS_URL=$(grep -oE 'https://[a-zA-Z0-9_-]+(\.run)?\.(pinggy-free\.link|pinggy\.link)' "$TUNNEL_LOG" 2>/dev/null | head -1)
        if [ -n "$HTTPS_URL" ]; then
            PROVIDER="Pinggy.io"
            break
        fi
        sleep 1
        ELAPSED=$((ELAPSED + 1))
    done
fi

echo ""
if [ -n "$HTTPS_URL" ]; then
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  ✅ ONLINE HTTPS AKTIF! ($PROVIDER)                              ║"
    echo "║                                                                  ║"
    echo "║  👉 $HTTPS_URL"
    echo "║                                                                  ║"
    echo "║  Token Ujian: KIMIA2026                                          ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "⚠️  Tekan Ctrl+C untuk menghentikan semua layanan."
else
    echo "❌ Semua provider tunnel gagal. Cek log detail:"
    echo "   Streamlit Log  : $STREAMLIT_LOG"
    echo "   Tunnel Log : $TUNNEL_LOG"
    kill $STREAMLIT_PID 2>/dev/null
    exit 1
fi

# --- Trap Ctrl+C to kill processes ---
cleanup() {
    echo ""
    echo "🛑 Menghentikan semua layanan..."
    kill $STREAMLIT_PID $TUNNEL_PID 2>/dev/null
    pkill -f "streamlit run.*$PORT" 2>/dev/null
    pkill -f "cloudflared tunnel" 2>/dev/null
    pkill -f "ssh.*ssh.localhost.run" 2>/dev/null
    pkill -f "ssh.*a.pinggy.io" 2>/dev/null
    echo "Selesai."
    exit 0
}

trap cleanup INT TERM

# --- Keep script alive ---
wait $TUNNEL_PID 2>/dev/null
