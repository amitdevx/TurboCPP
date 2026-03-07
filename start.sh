#!/bin/bash

# Navigate to the directory of the base
cd "$(dirname "$(readlink -f "$0")")" || { echo "Failed to navigate to base directory. Exiting.."; exit 1; }

# Check if DOSBox is present
[ -x "$(command -v dosbox)" ] || { echo "DOSBox not found, exiting.."; exit 1; }

# Display nice ASCII art :)
cat << EOF
+---------------------------------------------------------------+
|                                                               |
|    _____  _   _  ____   ____    ___     ____  ____   ____     |
|   |_   _|| | | ||  _ \ | __ )  / _ \   / ___||  _ \ |  _ \    |
|     | |  | | | || |_) |+  _ \ | | | | | |    | |_) |+ |_) |   |
|     | |  | |_| |+  _ < | |_) || |_| | | |___ |  __/ |  __/    |
|     |_|   \___/ |_| \_\|____/  \___/   \____||_|    |_|       |
|                                                               |
|        A port of Borland's C++ IDE for Linux machines,        |
|        using the popular DOSBOX Emulator, coz why not?        |
|                                                               |
+---------------------------------------------------------------+
|                                                               |
|  Please close this terminal window after you have had enough  |
|               of the awesome ASCII ART here :P                |
|                                                               |
|  Huge thanks to Vineeth Choudhary (@vineetchoudhary) for the  |
|          awesome TURBOC++ port for Windows machines.          |
|                                                               |
+---------------------------------------------------------------+
|      Check me out on GitHub: github.com/AvinashReddy3108      |
+---------------------------------------------------------------+
|                  ASCII Art: asciiflow.com                     |
+---------------------------------------------------------------+
EOF

# ─── TurboCPP AI: Start AI watcher in background ───────────────
AI_PID=""
if [ -f "${PWD}/ai/main.py" ] && [ -x "$(command -v python3)" ]; then
    AI_CONFIG="${PWD}/ai/config.json"
    # Only start if API key is configured (not empty)
    if [ -f "$AI_CONFIG" ] && python3 -c "
import json, sys
cfg = json.load(open('$AI_CONFIG'))
key = cfg.get('openrouter_api_key','')
sys.exit(0 if key else 1)
" 2>/dev/null; then
        echo ""
        echo "  ⚡ TurboCPP AI: Starting AI code assistant..."
        echo "  📝 Write '@ai <prompt>' in any .c/.cpp file to generate code!"
        echo ""
        python3 "${PWD}/ai/main.py" watch "${PWD}" > "${PWD}/ai/logs/watcher.log" 2>&1 &
        AI_PID=$!
        echo "  🤖 AI watcher running (PID: $AI_PID)"
        echo ""
    else
        echo ""
        echo "  💡 TurboCPP AI available but not configured."
        echo "  Run: python3 ai/main.py setup"
        echo ""
    fi
fi
# ────────────────────────────────────────────────────────────────

# Use project-local DOSBox config if it exists (CPU/perf optimizations)
DOSBOX_CONF=""
if [ -f "${PWD}/dosbox-turbo.conf" ]; then
    DOSBOX_CONF="-conf ${PWD}/dosbox-turbo.conf"
fi

# Start DOSBox — quotes around mount path handle spaces in directory names
dosbox ${DOSBOX_CONF} \
    -c "mount C \"${PWD}\"" \
    -c "SET PATH=%PATH%;C:\TC\BIN" \
    -c "C:" \
    -c "TC"

# ─── Cleanup: Stop AI watcher when DOSBox exits ────────────────
if [ -n "$AI_PID" ] && kill -0 "$AI_PID" 2>/dev/null; then
    echo "  Stopping AI watcher (PID: $AI_PID)..."
    kill "$AI_PID" 2>/dev/null
    wait "$AI_PID" 2>/dev/null
    echo "  ✓ AI watcher stopped."
fi
