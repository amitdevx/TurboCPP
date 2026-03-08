#!/bin/bash
# ================================================================
#  TurboCPP AI — One-Click Setup for Linux/macOS
#  Installs all dependencies and configures AI code generation.
# ================================================================

set -e

# Colors
R='\033[91m'; G='\033[92m'; Y='\033[93m'; C='\033[96m'; B='\033[1m'; X='\033[0m'

cd "$(dirname "$(readlink -f "$0")")" || exit 1
PROJECT_DIR="$(pwd)"

echo ""
echo -e "${C}╔══════════════════════════════════════════════════╗${X}"
echo -e "${C}║   ${Y}⚡ TurboCPP AI Setup${C}                            ║${X}"
echo -e "${C}║   One-Click Installer for Linux/macOS            ║${X}"
echo -e "${C}╚══════════════════════════════════════════════════╝${X}"
echo ""

ERRORS=0

# ─── Step 1: Check/Install DOSBox ────────────────────────────────
echo -e "${B}[1/4] Checking DOSBox...${X}"
if command -v dosbox &>/dev/null; then
    echo -e "  ${G}✓ DOSBox found: $(command -v dosbox)${X}"
else
    echo -e "  ${Y}DOSBox not found. Attempting to install...${X}"
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y -qq dosbox
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y dosbox
    elif command -v pacman &>/dev/null; then
        sudo pacman -Sy --noconfirm dosbox
    elif command -v brew &>/dev/null; then
        brew install dosbox
    else
        echo -e "  ${R}✗ Cannot auto-install DOSBox. Please install it manually:${X}"
        echo -e "    ${C}https://www.dosbox.com/download.php${X}"
        ERRORS=$((ERRORS + 1))
    fi
    if command -v dosbox &>/dev/null; then
        echo -e "  ${G}✓ DOSBox installed successfully${X}"
    fi
fi
echo ""

# ─── Step 2: Check/Install Python 3 ─────────────────────────────
echo -e "${B}[2/4] Checking Python 3...${X}"
PYTHON=""
for py in python3 python; do
    if command -v "$py" &>/dev/null; then
        ver=$("$py" --version 2>&1 | grep -oP '\d+\.\d+')
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
            PYTHON="$py"
            echo -e "  ${G}✓ Python found: $($py --version)${X}"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "  ${Y}Python 3.8+ not found. Attempting to install...${X}"
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y -qq python3 python3-pip
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3 python3-pip
    elif command -v pacman &>/dev/null; then
        sudo pacman -Sy --noconfirm python python-pip
    elif command -v brew &>/dev/null; then
        brew install python3
    else
        echo -e "  ${R}✗ Cannot auto-install Python. Please install Python 3.8+:${X}"
        echo -e "    ${C}https://www.python.org/downloads/${X}"
        ERRORS=$((ERRORS + 1))
    fi
    for py in python3 python; do
        if command -v "$py" &>/dev/null; then
            PYTHON="$py"
            echo -e "  ${G}✓ Python installed: $($py --version)${X}"
            break
        fi
    done
fi
echo ""

# ─── Step 3: Install Python packages ────────────────────────────
echo -e "${B}[3/4] Installing Python packages...${X}"
if [ -n "$PYTHON" ]; then
    PIP_FLAGS=""
    # Detect PEP 668 (externally managed environment)
    if $PYTHON -m pip install --dry-run watchdog 2>&1 | grep -q "externally-managed"; then
        PIP_FLAGS="--break-system-packages"
        echo -e "  ${Y}Note: Using --break-system-packages (PEP 668 system)${X}"
    fi

    $PYTHON -m pip install $PIP_FLAGS -q -r "$PROJECT_DIR/ai/requirements.txt" 2>&1 | tail -3
    if $PYTHON -c "import watchdog, requests" 2>/dev/null; then
        echo -e "  ${G}✓ watchdog and requests installed${X}"
    else
        echo -e "  ${R}✗ Package install failed. Try manually:${X}"
        echo -e "    ${C}$PYTHON -m pip install -r ai/requirements.txt${X}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "  ${R}✗ Skipped (Python not available)${X}"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# ─── Step 4: Create AI config and directories ───────────────────
echo -e "${B}[4/4] Setting up AI configuration...${X}"
mkdir -p "$PROJECT_DIR/ai/logs" "$PROJECT_DIR/ai/backups"

if [ ! -f "$PROJECT_DIR/ai/config.json" ]; then
    cp "$PROJECT_DIR/ai/config.example.json" "$PROJECT_DIR/ai/config.json"
    echo -e "  ${G}✓ Config created from template${X}"
else
    echo -e "  ${G}✓ Config already exists${X}"
fi

# Make start.sh executable
chmod +x "$PROJECT_DIR/start.sh" 2>/dev/null
echo -e "  ${G}✓ start.sh made executable${X}"

# Create TURBOC3 symlink (IDE expects C:\TURBOC3\ paths)
if [ ! -L "$PROJECT_DIR/TURBOC3" ]; then
    ln -sf TC "$PROJECT_DIR/TURBOC3"
    echo -e "  ${G}✓ TURBOC3 symlink created${X}"
else
    echo -e "  ${G}✓ TURBOC3 symlink already exists${X}"
fi

# Create SOURCE directory for IDE
mkdir -p "$PROJECT_DIR/TC/SOURCE"
echo ""

# ─── Summary ────────────────────────────────────────────────────
echo -e "${C}══════════════════════════════════════════════════${X}"
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${G}  ✓ Setup complete! All dependencies installed.${X}"
else
    echo -e "${Y}  ⚠ Setup finished with $ERRORS issue(s). See above.${X}"
fi
echo -e "${C}══════════════════════════════════════════════════${X}"
echo ""
echo -e "${B}Next steps:${X}"
echo -e "  1. Get your FREE API key from: ${C}https://openrouter.ai/keys${X}"
echo -e "  2. Run the AI setup wizard:    ${C}$PYTHON ai/main.py setup${X}"
echo -e "  3. Start TurboCPP with AI:     ${C}./start.sh${X}"
echo ""
echo -e "  Or configure and start in one go:"
echo -e "  ${C}$PYTHON ai/main.py setup && ./start.sh${X}"
echo ""
