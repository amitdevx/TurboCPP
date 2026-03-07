"""
TurboCPP AI - File Watcher
Monitors .c/.cpp files for @ai triggers and inserts generated code.
Works with DOSBox — handles DOS line endings, uppercase extensions,
and watches the correct directory where TC editor saves files.
"""

import os
import re
import time
import shutil
import logging
import threading
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger("turbocpp-ai")

AI_COMMENT_RE = re.compile(r"^\s*(?://|/\*)\s*@ai\s+(.+?)(?:\*/)?[\s\r]*$")
AI_GEN_START = "/* @ai-generated-start */"
AI_GEN_END = "/* @ai-generated-end */"

# Directories to ignore (never process files here)
IGNORE_DIRS = {"ai", ".git", "node_modules", "__pycache__", "venv"}


class AITrigger:
    """A detected @ai trigger in a source file."""
    def __init__(self, prompt, line_number, is_full_program=False):
        self.prompt = prompt
        self.line_number = line_number
        self.is_full_program = is_full_program


def parse_triggers(file_path):
    """Find all @ai comments in a file that haven't been processed yet."""
    triggers = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except (IOError, OSError) as e:
        logger.error(f"Cannot read {file_path}: {e}")
        return triggers

    if not lines:
        return triggers

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\r\n")
        m = AI_COMMENT_RE.match(line)
        if m:
            parts = [m.group(1).strip()]
            j = i + 1
            while j < len(lines):
                nline = lines[j].rstrip("\r\n")
                nm = AI_COMMENT_RE.match(nline)
                if nm and not nm.group(1).strip().startswith("-generated"):
                    parts.append(nm.group(1).strip())
                    j += 1
                else:
                    break

            prompt = " ".join(parts)

            # Skip if already has a generated block right after
            next_real = j
            while next_real < len(lines) and lines[next_real].strip() == "":
                next_real += 1
            if next_real < len(lines) and AI_GEN_START in lines[next_real]:
                i = j
                continue

            # Full program if file has no main() and prompt sounds like a full request
            content = "".join(lines)
            has_main = "main(" in content or "main (" in content
            full_kw = ["program", "write a", "create a", "make a", "build a", "print", "display", "simple"]
            is_full = any(k in prompt.lower() for k in full_kw) and not has_main

            triggers.append(AITrigger(prompt, i + 1, is_full))
            i = j
        else:
            i += 1
    return triggers


def insert_code(file_path, trigger, code, backup_dir=None):
    """Insert AI-generated code into the file after the @ai trigger."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        if backup_dir:
            _backup(file_path, backup_dir)

        if trigger.is_full_program:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code.rstrip() + "\n")
            logger.info(f"Full program written to {file_path}")
            return True

        # Find end of @ai comment block
        idx = trigger.line_number - 1 + 1
        while idx < len(lines):
            nline = lines[idx].rstrip("\r\n")
            if AI_COMMENT_RE.match(nline):
                t = AI_COMMENT_RE.match(nline).group(1).strip()
                if t.startswith("-generated"):
                    break
                idx += 1
            else:
                break

        indent = lines[trigger.line_number - 1][: len(lines[trigger.line_number - 1]) - len(lines[trigger.line_number - 1].lstrip())]
        block = (
            f"{indent}{AI_GEN_START}\n"
            + "\n".join(indent + l if l.strip() else l for l in code.split("\n"))
            + f"\n{indent}{AI_GEN_END}\n"
        )

        new_lines = lines[:idx] + [block] + lines[idx:]
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        logger.info(f"Code inserted into {file_path} at line {trigger.line_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to insert code: {e}")
        return False


def _backup(file_path, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)
    name = os.path.basename(file_path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(backup_dir, f"{name}.{ts}.bak")
    shutil.copy2(file_path, dst)
    logger.debug(f"Backup: {dst}")


def _in_ignored_dir(filepath, watch_root):
    """Check if file is inside an ignored directory."""
    try:
        rel = os.path.relpath(filepath, watch_root)
    except ValueError:
        return True
    parts = rel.replace("\\", "/").split("/")
    return any(p in IGNORE_DIRS for p in parts)


class _Handler(FileSystemEventHandler):
    """Watchdog handler for TurboCPP source files."""

    def __init__(self, generator, extensions, backup_dir, watch_root):
        super().__init__()
        self.generator = generator
        self.extensions = extensions
        self.backup_dir = backup_dir
        self.watch_root = watch_root
        self._debounce = {}
        self._processing = set()
        self._timers = {}

    def _should_handle(self, event):
        if event.is_directory:
            return False
        fp = event.src_path
        _, ext = os.path.splitext(fp)
        if ext.lower() not in self.extensions:
            return False
        if _in_ignored_dir(fp, self.watch_root):
            return False
        return True

    def on_modified(self, event):
        if self._should_handle(event):
            self._schedule_process(event.src_path)

    def on_created(self, event):
        if self._should_handle(event):
            self._schedule_process(event.src_path)

    def on_moved(self, event):
        if hasattr(event, 'dest_path'):
            fp = event.dest_path
            _, ext = os.path.splitext(fp)
            if ext.lower() in self.extensions and not _in_ignored_dir(fp, self.watch_root):
                self._schedule_process(fp)

    def _schedule_process(self, fp):
        """Delay processing to let DOSBox finish writing the file."""
        now = time.time()
        if fp in self._processing:
            return

        # Cancel any pending timer for this file
        if fp in self._timers:
            self._timers[fp].cancel()

        # Wait 1.5s after last event before processing (DOSBox debounce)
        self._debounce[fp] = now
        timer = threading.Timer(1.5, self._process, args=[fp])
        timer.daemon = True
        timer.start()
        self._timers[fp] = timer

    def _process(self, fp):
        if fp in self._processing:
            return
        self._processing.add(fp)
        self._timers.pop(fp, None)
        try:
            if not os.path.isfile(fp):
                return

            triggers = parse_triggers(fp)
            if not triggers:
                return

            logger.info(f"Found {len(triggers)} @ai trigger(s) in {os.path.basename(fp)}")

            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            for t in triggers:
                logger.info(f"  → Prompt: {t.prompt[:80]}")
                logger.info(f"  → Full program: {t.is_full_program}")
                if t.is_full_program:
                    code = self.generator.generate_full_program(t.prompt)
                else:
                    code = self.generator.generate_snippet(t.prompt, content)

                if code and "ERROR" not in code:
                    insert_code(fp, t, code, self.backup_dir)
                    logger.info(f"  ✓ Code generated and inserted")
                else:
                    logger.warning(f"  ✗ Generation failed: {code[:100] if code else 'empty'}")
        except Exception as e:
            logger.error(f"Error processing {fp}: {e}", exc_info=True)
        finally:
            self._processing.discard(fp)


def start_watcher(watch_dir, generator, extensions, backup_dir):
    """Start monitoring a directory for @ai triggers."""
    handler = _Handler(generator, extensions, backup_dir, watch_dir)
    observer = Observer()
    observer.schedule(handler, watch_dir, recursive=True)
    observer.start()
    logger.info(f"Watching: {watch_dir} (recursive, extensions: {extensions})")
    return observer
