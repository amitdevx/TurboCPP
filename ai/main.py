#!/usr/bin/env python3
"""
TurboCPP AI - Main Entry Point
AI-powered code generation integrated with Turbo C++ IDE.
Uses OpenRouter API (openrouter.ai) — FREE tier: 50 req/day.

Usage:
    python3 main.py watch [directory]    Watch for @ai triggers
    python3 main.py setup                Configure API key
    python3 main.py test                 Test AI connection
    python3 main.py generate "prompt"    One-shot code generation
    python3 main.py status               Show config status
"""

import os
import sys
import json
import signal
import logging
import argparse

AI_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(AI_DIR)
sys.path.insert(0, AI_DIR)

from src.ai_providers import OpenRouterProvider, fetch_free_models, get_free_model_ids
from src.code_generator import CodeGenerator
from src.file_watcher import start_watcher

CONFIG_FILE = os.path.join(AI_DIR, "config.json")
LOG_DIR = os.path.join(AI_DIR, "logs")
BACKUP_DIR = os.path.join(AI_DIR, "backups")

# ANSI colors (no dependency needed)
R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; C = "\033[96m"; B = "\033[1m"; X = "\033[0m"

# Fallback models if OpenRouter API is unreachable
FALLBACK_MODELS = [
    "google/gemma-3-12b-it:free",
    "google/gemma-3-27b-it:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-coder:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
]


def setup_logging(level="INFO"):
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(LOG_DIR, "turbocpp-ai.log")),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger("turbocpp-ai")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"{R}✗ Config not found. Run: python3 ai/main.py setup{X}")
        sys.exit(1)
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)


def banner():
    print(f"""
{C}╔══════════════════════════════════════════════════╗
║   {Y}⚡ TurboCPP AI{C}  v1.0.0                          ║
║   AI Code Generation for Turbo C++ IDE            ║
║   Powered by OpenRouter (FREE tier available)     ║
║   Write {G}@ai <prompt>{C} in any .c/.cpp file           ║
╚══════════════════════════════════════════════════╝{X}
""")


def cmd_setup(args):
    banner()
    print(f"{G}🔧 Setup Wizard{X}\n")

    cfg = load_config() if os.path.exists(CONFIG_FILE) else {
        "openrouter_api_key": "",
        "model": "google/gemma-3-12b-it:free",
        "watch_extensions": [".c", ".cpp", ".h"],
        "backup_enabled": True, "log_level": "INFO",
        "max_tokens": 2048, "temperature": 0.3,
    }

    print(f"  Get your FREE API key from: {C}https://openrouter.ai/keys{X}")
    print(f"  Free tier: 50 requests/day, 20 requests/minute\n")

    key = input(f"Enter OpenRouter API key: ").strip()
    if key:
        cfg["openrouter_api_key"] = key

    # Fetch available models dynamically
    print(f"\n{Y}Fetching available free models from OpenRouter...{X}")
    models = get_free_model_ids()
    if not models:
        print(f"{Y}Could not fetch models, using fallback list.{X}")
        models = FALLBACK_MODELS

    print(f"\n{G}Available FREE models ({len(models)} found):{X}")
    display_count = min(len(models), 15)
    for i, m in enumerate(models[:display_count], 1):
        marker = " ← current" if m == cfg.get("model") else ""
        print(f"  {C}{i}{X}. {m}{marker}")
    if len(models) > display_count:
        print(f"  {Y}... and {len(models) - display_count} more{X}")

    choice = input(f"\nSelect model [{Y}1{X}] (or type model name): ").strip() or "1"
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(models):
            cfg["model"] = models[idx]
    except ValueError:
        if "/" in choice:
            cfg["model"] = choice

    save_config(cfg)
    print(f"\n{G}✓ Configuration saved!{X}")
    print(f"  Model: {C}{cfg['model']}{X}")
    print(f"\nStart TurboCPP with AI:  {C}./start.sh{X}")
    print(f"Or run watcher manually: {C}python3 ai/main.py watch{X}\n")


def _make_provider(cfg):
    if not cfg.get("openrouter_api_key"):
        print(f"{R}✗ No API key. Run: python3 ai/main.py setup{X}")
        sys.exit(1)
    return OpenRouterProvider(cfg)


def cmd_watch(args):
    banner()
    cfg = load_config()
    logger = setup_logging(cfg.get("log_level", "INFO"))

    # Watch project root — DOSBox mounts it as C:\ and TC editor saves there
    watch_dir = args.directory or PROJECT_ROOT
    watch_dir = os.path.expanduser(watch_dir)

    if not os.path.isdir(watch_dir):
        print(f"{R}✗ Directory not found: {watch_dir}{X}")
        sys.exit(1)

    provider = _make_provider(cfg)
    generator = CodeGenerator(provider)
    exts = cfg.get("watch_extensions", [".c", ".cpp", ".h"])
    bdir = BACKUP_DIR if cfg.get("backup_enabled", True) else None

    print(f"{G}👁  Watching:{X}  {watch_dir}")
    print(f"{G}🤖 Model:   {X}  {provider.get_name()}")
    print(f"{G}📄 Files:   {X}  {', '.join(exts)}")
    print(f"\n{Y}Write '@ai <prompt>' in any .c/.cpp file and save — AI generates code!{X}")
    print(f"{Y}Press Ctrl+C to stop.{X}\n")

    observer = start_watcher(watch_dir, generator, exts, bdir)

    def stop(sig, frame):
        print(f"\n{Y}Stopping watcher...{X}")
        observer.stop()
        observer.join()
        print(f"{G}✓ Stopped.{X}")
        sys.exit(0)

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    try:
        while observer.is_alive():
            observer.join(timeout=1)
    except KeyboardInterrupt:
        stop(None, None)


def cmd_generate(args):
    banner()
    cfg = load_config()
    provider = _make_provider(cfg)
    generator = CodeGenerator(provider)

    prompt = " ".join(args.prompt)
    print(f"{C}Generating:{X} {prompt}\n")

    code = generator.generate_full_program(prompt)
    print(f"{G}{'─' * 50}")
    print(code)
    print(f"{'─' * 50}{X}")

    if args.output:
        with open(args.output, "w") as f:
            f.write(code + "\n")
        print(f"\n{G}✓ Saved to {args.output}{X}")


def cmd_test(args):
    banner()
    print(f"{Y}Testing OpenRouter connection...{X}\n")
    cfg = load_config()
    provider = _make_provider(cfg)
    generator = CodeGenerator(provider)

    print(f"Model: {C}{provider.get_name()}{X}")
    print(f"Sending test prompt: {C}'Hello World program'{X}\n")

    code = generator.generate_full_program("hello world program that prints Hello World on screen")

    if code and "ERROR" not in code:
        print(f"{G}✓ Connection successful!{X}\n")
        print(code)
    else:
        print(f"{R}✗ Failed:{X}\n{code}")


def cmd_status(args):
    banner()
    if not os.path.exists(CONFIG_FILE):
        print(f"{R}✗ Not configured. Run: python3 ai/main.py setup{X}")
        return
    cfg = load_config()
    has_key = bool(cfg.get("openrouter_api_key"))
    print(f"  API Key:   {G + '✓ set' if has_key else R + '✗ missing'}{X}")
    print(f"  Model:     {C}{cfg.get('model', 'not set')}{X}")
    print(f"  Watch Dir: {C}{PROJECT_ROOT}{X}")
    print(f"  Backup:    {G}{'on' if cfg.get('backup_enabled') else 'off'}{X}")
    print()


def cmd_models(args):
    banner()
    print(f"{Y}Fetching available free models from OpenRouter...{X}\n")
    models = fetch_free_models()
    if not models:
        print(f"{R}✗ Could not fetch models. Check internet connection.{X}")
        return

    cfg = load_config() if os.path.exists(CONFIG_FILE) else {}
    current = cfg.get("model", "")

    print(f"{G}Available FREE models ({len(models)}):{X}\n")
    for i, m in enumerate(models, 1):
        marker = f" {G}← active{X}" if m["id"] == current else ""
        ctx = f" ({m['context_length']}ctx)" if m["context_length"] else ""
        print(f"  {C}{i:2d}{X}. {m['id']}{ctx}{marker}")

    print(f"\n{Y}Tip:{X} Run {C}python3 ai/main.py setup{X} to change model\n")


def main():
    p = argparse.ArgumentParser(description="TurboCPP AI — Code Generation for Turbo C++ (via OpenRouter)")
    sub = p.add_subparsers(dest="command")

    sub.add_parser("setup", help="Configure OpenRouter API key")

    wp = sub.add_parser("watch", help="Watch for @ai triggers")
    wp.add_argument("directory", nargs="?", help="Directory to watch (default: TC/)")

    gp = sub.add_parser("generate", help="Generate code from prompt")
    gp.add_argument("prompt", nargs="+", help="Code prompt")
    gp.add_argument("-o", "--output", help="Output file")

    sub.add_parser("test", help="Test AI connection")
    sub.add_parser("status", help="Show configuration")
    sub.add_parser("models", help="List available free models")

    args = p.parse_args()
    cmds = {"setup": cmd_setup, "watch": cmd_watch, "generate": cmd_generate,
            "test": cmd_test, "status": cmd_status, "models": cmd_models}

    if args.command in cmds:
        cmds[args.command](args)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
