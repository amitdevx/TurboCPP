"""
TurboCPP AI - File Watcher
Monitors .c/.cpp files for @ai triggers and inserts generated code.
"""

import os
import re
import time
import shutil
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger("turbocpp-ai")

AI_COMMENT_RE = re.compile(r"^\s*(?://|/\*)\s*@ai\s+(.+?)(?:\*/)?$")
AI_GEN_START = "/* @ai-generated-start */"
AI_GEN_END = "/* @ai-generated-end */"


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

    i = 0
    while i < len(lines):
        m = AI_COMMENT_RE.match(lines[i])
        if m:
            parts = [m.group(1).strip()]
            j = i + 1
            # Collect continuation @ai lines
            while j < len(lines):
                nm = AI_COMMENT_RE.match(lines[j])
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
            full_kw = ["program", "write a", "create a", "make a", "build a"]
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
            # Replace entire file with generated program
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code + "\n")
            return True

        # Find end of @ai comment block
        idx = trigger.line_number - 1 + 1
        while idx < len(lines):
            if AI_COMMENT_RE.match(lines[idx]):
                t = AI_COMMENT_RE.match(lines[idx]).group(1).strip()
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


class _Handler(FileSystemEventHandler):
    """Watchdog handler for TurboCPP source files."""

    def __init__(self, generator, extensions, backup_dir):
        super().__init__()
        self.generator = generator
        self.extensions = extensions
        self.backup_dir = backup_dir
        self._debounce = {}
        self._processing = set()

    def on_modified(self, event):
        if event.is_directory:
            return
        fp = event.src_path
        _, ext = os.path.splitext(fp)
        if ext.lower() not in self.extensions:
            return

        now = time.time()
        if now - self._debounce.get(fp, 0) < 2.0:
            return
        self._debounce[fp] = now

        if fp in self._processing:
            return
        self._process(fp)

    def _process(self, fp):
        self._processing.add(fp)
        try:
            triggers = parse_triggers(fp)
            if not triggers:
                return

            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            logger.info(f"Found {len(triggers)} @ai trigger(s) in {os.path.basename(fp)}")

            for t in triggers:
                logger.info(f"  → {t.prompt[:70]}...")
                if t.is_full_program:
                    code = self.generator.generate_full_program(t.prompt)
                else:
                    code = self.generator.generate_snippet(t.prompt, content)

                if code:
                    insert_code(fp, t, code, self.backup_dir)
                    logger.info(f"  ✓ Done")
                else:
                    logger.warning(f"  ✗ No code generated")
        except Exception as e:
            logger.error(f"Error processing {fp}: {e}")
        finally:
            self._processing.discard(fp)


def start_watcher(watch_dir, generator, extensions, backup_dir):
    """Start monitoring a directory for @ai triggers."""
    handler = _Handler(generator, extensions, backup_dir)
    observer = Observer()
    observer.schedule(handler, watch_dir, recursive=True)
    observer.start()
    logger.info(f"Watching: {watch_dir}")
    return observer
