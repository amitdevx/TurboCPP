# SOLUTION: Ctrl+F9 "Quits Immediately" Issue

## Root Cause Identified ✅

**The .gitignore file was excluding C0*.OBJ startup files!**

```gitignore
# .gitignore (line 8-9)
*.OBJ          # ← Excludes ALL .OBJ files
*.EXE
!TC/BIN/*.EXE
```

This prevented essential TC/LIB/C0*.OBJ files from being committed to the repository.

### What Was Happening
1. ✅ Compilation: `test.c` → `test.OBJ` (success)
2. ❌ Linking: `test.OBJ` → `test.EXE` (FAILS - no C0S.OBJ)
3. 💥 Ctrl+F9 tries to run non-existent .EXE → appears to "quit immediately"

### Evidence
```bash
$ find TC -name "*.OBJ" | wc -l
0   # ← NO object files in TC/

$ ls -la *.OBJ
NONAME00.OBJ  TEST8.OBJ   # Compiled successfully

$ ls -la *.EXE
# NONE! Linking failed
```

## Solution

### Step 1: Fix .gitignore (DONE ✅)

Updated `.gitignore` to allow TC/LIB/*.OBJ:

```gitignore
*.OBJ
!TC/LIB/*.OBJ    # ← NEW: Allow startup files
*.EXE
!TC/BIN/*.EXE
```

### Step 2: Download Missing Files

You need to add C0*.OBJ files to TC/LIB/:

#### Option A: Download from Archive.org
1. Download Turbo C++ 3.0:
   https://archive.org/details/msdos_borland_turbo_cpp_3.0

2. Extract and copy files:
   ```bash
   # Extract TC30.zip
   unzip TC30.zip
   
   # Copy ONLY .OBJ files to TC/LIB/
   cp TC_FROM_ARCHIVE/LIB/*.OBJ ./TC/LIB/
   ```

3. Verify:
   ```bash
   ls -la TC/LIB/C0*.OBJ
   # Should list: C0S.OBJ, C0C.OBJ, C0M.OBJ, C0L.OBJ, C0H.OBJ
   ```

#### Option B: Use Pre-Built Package
If someone has already created a TC folder with all files:
```bash
# Download complete TC folder
wget https://example.com/TC_COMPLETE.tar.gz
tar -xzf TC_COMPLETE.tar.gz

# Backup your current TC
mv TC TC.backup

# Use complete version
mv TC_COMPLETE TC

# Restore your config
cp TC.backup/BIN/TCCONFIG.TC TC/BIN/
```

### Step 3: Commit Files to Git

Once C0*.OBJ files are in TC/LIB/:

```bash
# Verify they're now tracked
git status TC/LIB/

# Should show:
#   new file:   TC/LIB/C0C.OBJ
#   new file:   TC/LIB/C0H.OBJ
#   new file:   TC/LIB/C0L.OBJ
#   new file:   TC/LIB/C0M.OBJ
#   new file:   TC/LIB/C0S.OBJ
#   ... etc

# Commit
git add TC/LIB/*.OBJ
git add .gitignore
git commit -m "fix: add missing C0*.OBJ startup files for linking

- Updated .gitignore to allow TC/LIB/*.OBJ
- Added C0S.OBJ, C0C.OBJ, C0M.OBJ, C0L.OBJ, C0H.OBJ
- Fixes Ctrl+F9 'quits immediately' issue (linking now works)"

git push
```

### Step 4: Verify Fix

Test that Ctrl+F9 now works:

```bash
# Start Turbo C++
./start.sh

# In IDE:
1. Open test_simple.c
2. Press Ctrl+F9
3. Should now see:
   - "Compiling..." message
   - "Linking..." message
   - Black DOS screen appears
   - Program output displays
   - Waits for keypress
   - Returns to IDE

# Also verify .EXE created:
$ ls -la *.EXE
-rw-rw-r-- 1 user user 8192 Mar  8 12:20 NONAME00.EXE  # ← SUCCESS!
```

## Files You Need

### Minimum Required (6 files)
```
TC/LIB/C0S.OBJ    ~2KB   Small model
TC/LIB/C0C.OBJ    ~2KB   Compact model  
TC/LIB/C0M.OBJ    ~2KB   Medium model
TC/LIB/C0L.OBJ    ~2KB   Large model
TC/LIB/C0H.OBJ    ~2KB   Huge model
TC/LIB/C0T.OBJ    ~1KB   Tiny model (optional)
```

### Recommended Additional Files
```
TC/LIB/FP87.OBJ       Floating point (8087 math coprocessor)
TC/LIB/EMU.OBJ        Floating point emulator
TC/LIB/WILDARGS.OBJ   Wildcard expansion for command line
TC/LIB/SETARGV.OBJ    Alternative argv[] handling
```

## Why This Issue Occurred

1. **Original developer** included TC folder in repo
2. Added `*.OBJ` to `.gitignore` to exclude build artifacts
3. **Unintended consequence**: Also excluded TC/LIB/C0*.OBJ (runtime files)
4. When you cloned the repo, you got incomplete TC installation
5. Programs compiled but couldn't link

## Prevention for Future

If maintaining this repo:

```gitignore
# Be specific about what to exclude:
NONAME*.OBJ       # Build artifacts
TEST*.OBJ         # User test files
*.BAK             # Backups

# Allow runtime files:
!TC/LIB/*.OBJ     # Startup and runtime objects
!TC/BIN/*.EXE     # TC executables
```

## Alternative: Store TC Outside Repo

Better approach for large projects:

1. Don't commit TC folder at all
2. Document in README: "Download TC 3.0 from archive.org"
3. Provide setup script that downloads/extracts TC
4. Only commit: dosbox-turbo.conf, start.sh, ai/ folder

This avoids large binary files in git history.

## Testing Checklist

After adding C0*.OBJ files:

- [ ] `ls TC/LIB/C0*.OBJ` shows 5+ files
- [ ] Start TC IDE with `./start.sh`
- [ ] Open test_simple.c
- [ ] Press Ctrl+F9
- [ ] See "Compiling..." then "Linking..."
- [ ] Program runs and displays output
- [ ] Press key to return to IDE
- [ ] Exit IDE and verify: `ls *.EXE` shows NONAME00.EXE
- [ ] Run directly: `./start.sh` then `NONAME00.EXE` works

All ✅ = Fixed!

## Quick Reference

| Symptom | Diagnosis | Fix |
|---------|-----------|-----|
| Ctrl+F9 quits instantly | No .EXE created | Add C0*.OBJ to TC/LIB/ |
| "Cannot open C0S.OBJ" | Missing startup file | Download from TC 3.0 archive |
| Compiles but won't link | .gitignore blocking | Update .gitignore exception |
| "Undefined symbol" errors | Missing .LIB files | Check TC/LIB/*.LIB exists |

## Links

- Turbo C++ 3.0: https://archive.org/details/msdos_borland_turbo_cpp_3.0
- WinWorld: https://winworldpc.com/product/turbo-c/3x
- DOSBox: https://www.dosbox.com/
- This repo: https://github.com/amitdevx/TurboCPP

---

**Status**: .gitignore fixed ✅  
**Next**: Add C0*.OBJ files to TC/LIB/ (see Option A above)  
**Then**: Test Ctrl+F9 and commit files
