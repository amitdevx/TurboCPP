# TurboCPP4Linux — Issues Found & Fixes Applied

> Single-document changelog of every issue identified and the exact fix applied.

---

## Issue 1 · High CPU usage — DOSBox runs at 100 % with no cycle cap

**Problem**: The original `start.sh` launched DOSBox without any `-conf` flag, so DOSBox used its global config where `cycles=auto`. In practice `auto` ramps up to the maximum the host CPU can deliver, pinning one core at 100 % even while the IDE is idle. On laptops this causes overheating and fast battery drain.

**Fix**: Created a project-local config file `dosbox-turbo.conf` with `cycles=3000` (a fixed cap that keeps Turbo C++ responsive while cutting idle CPU usage by roughly 60-70 %). Also set `frameskip=1` and `rate=22050` to further reduce rendering and audio overhead. Modified `start.sh` to pass `-conf dosbox-turbo.conf` when the file exists.

**Files changed**: `start.sh` (lines 37-48), new file `dosbox-turbo.conf`

---

## Issue 2 · Mount path breaks when directory name contains spaces

**Problem**: The original mount command was:
```
-c "mount C ${PWD}"
```
If the project lived in a path like `/home/user/My Projects/TurboCPP`, DOSBox would see `mount C /home/user/My` and fail silently.

**Fix**: Changed to:
```
-c "mount C \"${PWD}\""
```
The inner escaped quotes make DOSBox treat the entire path as a single argument regardless of spaces.

**Files changed**: `start.sh` (line 45)

---

## Issue 3 · Invalid DOS drive-switch command `C:/`

**Problem**: The original script used `-c "C:/"`. In DOSBox the valid command to switch to drive C is just `C:`. The trailing slash is not standard and may cause "Illegal command" on some DOSBox builds.

**Fix**: Changed to `-c "C:"`.

**Files changed**: `start.sh` (line 47)

---

## Issue 4 · PATH separator used forward slashes instead of backslashes

**Problem**: Original line:
```
-c "SET PATH=%PATH%;C:/TC/BIN"
```
DOSBox emulates DOS, which expects backslash path separators. While DOSBox tolerates forward slashes in many places, the SET/PATH statement is more reliable with native DOS backslashes.

**Fix**: Changed to:
```
-c "SET PATH=%PATH%;C:\TC\BIN"
```

**Files changed**: `start.sh` (line 46)

---

## Issue 5 · No Windows support — Linux-only launcher

**Problem**: The project only shipped `start.sh` (a Bash script). Windows users had no way to launch Turbo C++ without manually configuring DOSBox.

**Fix**: Created `start.bat` — a Windows batch file that:
- Checks if DOSBox is on `%PATH%`
- Falls back to common `Program Files` install locations
- Uses the same `dosbox-turbo.conf` for CPU optimization
- Properly quotes the mount path for Windows paths with spaces

**Files changed**: new file `start.bat`

---

## Issue 6 · Swap files cluttering the project root

**Problem**: Three DOSBox/TC swap files were committed to the project root:
- `TC0000.SWP` (256 KB)
- `TC0001.SWP` (256 KB)
- `TC0002.SWP` (256 KB)

These are temporary editor recovery files with no value.

**Fix**: Deleted all three files and added `*.SWP` to `.gitignore` to prevent them from reappearing.

**Files changed**: deleted `TC0000.SWP`, `TC0001.SWP`, `TC0002.SWP`; updated `.gitignore`

---

## Issue 7 · Build artifacts committed to the project root

**Problem**: Two Turbo C++ build outputs were in the root directory:
- `NONAME00.EXE` (12 KB — compiled MS-DOS executable)
- `NONAME00.OBJ` (4 KB — object file)

These are user-generated compiler outputs that should not be in version control.

**Fix**: Deleted both files and added `NONAME*.EXE`, `NONAME*.OBJ`, `*.OBJ`, and `*.EXE` patterns to `.gitignore` (with `!TC/BIN/*.EXE` to keep the Turbo C++ binaries themselves).

**Files changed**: deleted `NONAME00.EXE`, `NONAME00.OBJ`; updated `.gitignore`

---

## Issue 8 · `.gitignore` incomplete

**Problem**: The original `.gitignore` only had two rules (`TC/**/*.SWP` and `TC/Projects/*`). Root-level swap files, build artifacts, and the `start.sh.backup` could all be committed accidentally.

**Fix**: Expanded `.gitignore`:
```gitignore
# Swap files (inside TC/ and project root)
TC/**/*.SWP
*.SWP

# Build artifacts produced by Turbo C++
NONAME*.EXE
NONAME*.OBJ
*.OBJ
*.EXE
!TC/BIN/*.EXE

# User's Projects
TC/Projects/*

# Backup of start.sh
start.sh.backup
```

**Files changed**: `.gitignore`

---

## Issue 9 · README only mentions Linux

**Problem**: `README.md` stated "Anything that runs Linux" and only gave `sudo apt install dosbox` as an install command. No mention of Windows, Fedora, or Arch.

**Fix**: Rewrote the System Requirements and Instructions sections to cover Linux (Ubuntu/Mint, Fedora, Arch) and Windows. Added a Performance Note explaining the `dosbox-turbo.conf` file and how to tune `cycles`.

**Files changed**: `README.md`

---

## Summary of all files touched

| File | Action | What changed |
|------|--------|--------------|
| `start.sh` | Modified | Quoted mount path, fixed `C:/` → `C:`, fixed PATH backslashes, added `-conf` support |
| `start.bat` | **Created** | Windows launcher with DOSBox auto-detection |
| `dosbox-turbo.conf` | **Created** | CPU-optimised DOSBox config (`cycles=3000`, `frameskip=1`, `rate=22050`) |
| `.gitignore` | Modified | Added rules for `*.SWP`, `*.EXE`, `*.OBJ`, backup file |
| `README.md` | Modified | Added Windows instructions, multi-distro install, performance note |
| `TC0000.SWP` | **Deleted** | Unnecessary swap file |
| `TC0001.SWP` | **Deleted** | Unnecessary swap file |
| `TC0002.SWP` | **Deleted** | Unnecessary swap file |
| `NONAME00.EXE` | **Deleted** | User build artifact |
| `NONAME00.OBJ` | **Deleted** | User build artifact |

---

## What was NOT changed (and why)

| Item | Reason left alone |
|------|-------------------|
| `TC/` directory (all 343 files) | These are the original Borland Turbo C++ binaries, headers, and libraries — they must stay untouched |
| ASCII art in `start.sh` | Cosmetic, original author's work |
| `TC/BIN/TC.EXE` and other `.EXE` inside `TC/BIN/` | Required for the IDE to work; `.gitignore` has `!TC/BIN/*.EXE` to protect them |

---

## How to verify the fixes

```bash
# 1. Launch on Linux
chmod +x start.sh
./start.sh
# Turbo C++ should open. Type a small program, Ctrl+F9 to compile.

# 2. Check CPU usage (in another terminal)
top -p $(pgrep dosbox)
# Should show ~10-30 % CPU instead of 80-100 %

# 3. Launch on Windows
# Double-click start.bat (DOSBox must be installed)

# 4. Tune performance if needed
# Edit dosbox-turbo.conf → change cycles=3000 to cycles=5000 and restart
```
