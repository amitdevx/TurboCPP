# CRITICAL: Incomplete Turbo C++ Installation

## Problem Identified
Ctrl+F9 fails because **startup object files are missing** from TC/LIB/.

### Current State
```
TC/LIB/ directory: ✅ Has .LIB files (CS.LIB, CL.LIB, etc.)
                   ❌ Missing ALL .OBJ files (C0S.OBJ, C0C.OBJ, etc.)
Result: Compilation works, but linking fails → No .EXE created
```

### Evidence
```bash
$ find TC -name "*.OBJ" | wc -l
0   # ← ZERO object files!

$ ls -la *.OBJ
NONAME00.OBJ  # Compiled successfully
TEST8.OBJ     # Compiled successfully

$ ls -la *.EXE
# NONE! Linking failed due to missing C0*.OBJ
```

## Required Files (Missing)

### Startup Files (C0*.OBJ)
- **C0S.OBJ** - Small model startup (~2KB)
- **C0C.OBJ** - Compact model startup (~2KB)
- **C0M.OBJ** - Medium model startup (~2KB)
- **C0L.OBJ** - Large model startup (~2KB)
- **C0H.OBJ** - Huge model startup (~2KB)
- **C0T.OBJ** - Tiny model startup (~1KB)

These files contain the program entry point (`_main`) and runtime initialization code that every C program needs before calling your `main()` function.

### Runtime Files (CRT)
Should also have various runtime .OBJ files in TC/LIB/ for:
- I/O functions (printf, scanf)
- Memory management (malloc, free)
- String functions (strcpy, strlen)
- Math functions

## How To Fix

### Option 1: Get Complete Turbo C++ 3.0 Installation

1. Download **complete** Turbo C++ 3.0 from archive:
   - https://archive.org/details/msdos_borland_turbo_cpp_3.0
   - Or: https://winworldpc.com/product/turbo-c/3x

2. Extract and copy ONLY the missing files:
   ```bash
   # From downloaded TC installation:
   cp /path/to/complete/TC/LIB/*.OBJ ./TC/LIB/
   ```

3. Verify:
   ```bash
   ls -la TC/LIB/C0*.OBJ
   # Should show: C0S.OBJ, C0C.OBJ, C0M.OBJ, C0L.OBJ, C0H.OBJ
   ```

### Option 2: Replace Entire TC Folder

1. Backup current TC folder:
   ```bash
   mv TC TC.backup
   ```

2. Extract complete Turbo C++ 3.0 to new TC folder

3. Restore any custom configurations:
   ```bash
   cp TC.backup/BIN/TCCONFIG.TC TC/BIN/
   cp TC.backup/BIN/TURBOC.CFG TC/BIN/
   ```

### Option 3: Use Older Turbo C Installation

If you have Turbo C 2.01 or similar:
- Also requires C0*.OBJ files
- Same linking process
- Download from: https://archive.org/details/msdos_borland_turbo_c_2.01

## Verification After Fix

Test that linking now works:

```bash
# Start DOSBox
./start.sh

# In DOSBox prompt:
C:\> TC\BIN\TCC test_simple.c
C:\> DIR *.EXE
# Should now show: test_simple.exe

C:\> test_simple.exe
# Should run and display output!
```

Or test linking manually:
```dos
C:\> TC\BIN\TCC -c test_simple.c
# Creates test_simple.OBJ

C:\> TC\BIN\TLINK TC\LIB\C0S.OBJ test_simple.OBJ,test_simple.EXE,,TC\LIB\CS.LIB
# Should create test_simple.exe WITHOUT errors
```

If you see errors like:
- "Cannot open file 'C0S.OBJ'" → Files still missing
- "Undefined symbol 'printf'" → .LIB files issue
- Success with no errors → Fixed!

## Why This Happened

Possible causes of incomplete installation:
1. **Incomplete git clone** - If TC folder was in repo, some files might have been skipped
2. **Partial extraction** - Archive.org download incomplete
3. **Corrupted files** - Download or transfer error
4. **.gitignore excluding .OBJ** - If TC was committed to git, .OBJ files might be ignored

Check `.gitignore`:
```bash
cat .gitignore | grep -i obj
```

If it says `*.OBJ` or `*.obj`, that's the problem! Object files were excluded from the repository.

## Temporary Workaround (NOT RECOMMENDED)

If you need to test immediately without full installation:

1. Download just C0S.OBJ (small model):
   - Extract from archive.org TC 3.0 download
   - Place in: TC/LIB/C0S.OBJ

2. Configure IDE to use Small model only:
   - Alt+O → Compiler → Code Generation → Model: Small
   - This uses C0S.OBJ for all programs

3. Link manually:
   ```dos
   TC\BIN\TLINK TC\LIB\C0S.OBJ yourprogram.OBJ,yourprogram.EXE,,TC\LIB\CS.LIB
   ```

This lets you compile simple programs but NOT recommended for anything serious.

## After Installing Missing Files

Once C0*.OBJ files are in TC/LIB/:

1. Test compilation in IDE:
   ```
   - Open test_simple.c
   - Press Ctrl+F9
   - Should now work correctly!
   ```

2. Verify .EXE created:
   ```bash
   ls -la *.EXE
   # Should show: NONAME00.EXE or test_simple.exe
   ```

3. Run directly:
   ```dos
   C:\> NONAME00.EXE
   Hello World!
   Press any key...
   ```

## Reference: Complete TC/LIB Contents

A proper TC/LIB directory should contain:

### Object Files (~15-20 files)
```
C0S.OBJ    C0C.OBJ    C0M.OBJ    C0L.OBJ    C0H.OBJ    C0T.OBJ
FP87.OBJ   EMU.OBJ    WILDARGS.OBJ  SETARGV.OBJ
```

### Library Files (~20-30 files)
```
CS.LIB     CC.LIB     CM.LIB     CL.LIB     CH.LIB     (C runtime)
MATHS.LIB  MATHC.LIB  MATHM.LIB  MATHL.LIB  MATHH.LIB  (Math)
GRAPHICS.LIB  (BGI graphics)
FP87.LIB   EMU.LIB    (Floating point)
```

Check yours:
```bash
ls TC/LIB/*.OBJ | wc -l  # Should be > 10
ls TC/LIB/*.LIB | wc -l  # Should be > 15
```

## Contact

If you continue having issues after adding C0*.OBJ files:
- Check: https://github.com/amitdevx/TurboCPP/issues
- Provide output of: `ls -la TC/LIB/`
