# Fix for Ctrl+F9 Quitting Immediately

## ⚠️ ACTUAL ROOT CAUSE FOUND

**CRITICAL**: Your Turbo C++ installation is **INCOMPLETE**!

### Missing Files
The `TC/LIB/` directory is missing **ALL startup object files** (C0*.OBJ):
- C0S.OBJ (Small model)
- C0C.OBJ (Compact model)
- C0M.OBJ (Medium model)
- C0L.OBJ (Large model)
- C0H.OBJ (Huge model)

### What's Happening
1. ✅ Compilation succeeds → Creates .OBJ file
2. ❌ Linking FAILS → Cannot create .EXE (no startup code)
3. Ctrl+F9 tries to run non-existent .EXE → Appears to "quit immediately"

### Verification
```bash
ls -la TC/LIB/C0*.OBJ  # Should list 5+ files
# Result: "No such file or directory" ← PROBLEM!

ls -la *.OBJ           # Check current directory
# Shows: NONAME00.OBJ, TEST8.OBJ (compiled but not linked)

ls -la *.EXE           # Check for executables
# Result: None! (linking fails)
```

## Solution: Complete Turbo C++ Installation Required

Your TC folder is only 8.3MB. A complete installation should be ~12-15MB.

When TC++ runs a program, it needs to:
1. Save the IDE screen (blue interface)
2. Switch to DOS text mode (black screen)  
3. Run your .EXE program
4. Show program output
5. Wait for program to finish (getch())
6. Switch back to IDE screen

Under DOSBox, the display swapping might not work correctly, causing your program to run in the background while the IDE screen stays visible. The program executes and finishes instantly (from your perspective) because you never see its output.

## Solution: Configure Display Swapping in IDE

### Step 1: Open Turbo C++ IDE
```bash
./start.sh
```

### Step 2: Access Options Menu
- Press `Alt + O` (Options menu)
- Or click "Options" in the menu bar

### Step 3: Go to Debugger Settings
- Select "Debugger" or press `D`

### Step 4: Set Display Swapping
- Find "Display swapping" option
- Set it to: **"Always"** (not "Smart" or "None")

Options explained:
- **None**: No display swapping (fastest, but programs invisible)
- **Smart**: Swap only when needed (default, can fail in DOSBox)
- **Always**: Always swap (slowest, but most reliable) ← **USE THIS**

### Step 5: Save Configuration
- Press `Alt + O` → `S` (Options → Save)
- Or: Options → Save options

This saves to `TC\BIN\TCCONFIG.TC`

### Step 6: Test
1. Open any `.c` file (e.g., `test_simple.c`)
2. Press `Ctrl + F9` (Compile & Run)
3. You should now see:
   - Black DOS screen appears
   - Program output displays
   - "Press any key..." waits for input
   - After key press, returns to blue IDE

## Alternative: Compile and Run Outside IDE

If the above doesn't work, compile and run manually:

### Method 1: Use Alt+F9 + Manual Run
1. Press `Alt + F9` (Compile only, no run)
2. Exit TC IDE (`Alt + X`)
3. At DOSBox prompt, type: `NONAME00.EXE` (or your program name)
4. See output, press key, then type `TC` to return to IDE

### Method 2: Use Command-Line Compiler
Exit IDE and use TCC.EXE:
```dos
C:\> TC\BIN\TCC test_simple.c
C:\> test_simple.exe
```

## DOSBox Configuration Tweaks

If display swapping still doesn't work, try these in `dosbox-turbo.conf`:

### Option A: Change video output mode
```ini
[sdl]
output=overlay    # Try: overlay, opengl, openglnb, ddraw
```

### Option B: Increase machine speed
```ini
[cpu]
cycles=8000       # Up from 3000 (faster display updates)
```

### Option C: Change machine type
```ini
[dosbox]
machine=vgaonly   # Try: vgaonly, svga_et4000, svga_et3000
```

## Verify It Works

Test with this simple program:

```c
#include <stdio.h>
#include <conio.h>

void main()
{
    clrscr();
    printf("Hello from Turbo C++!\n");
    printf("\n");
    printf("If you can see this, display swapping works!\n");
    printf("\n");
    printf("Press any key to return to IDE...");
    getch();
}
```

Save as `TEST_DISPLAY.C`, press Ctrl+F9. You should see the output clearly.

## Technical Background

### Why This Happens
- **Turbo C++ (1992)** was designed for real DOS, not emulators
- It uses direct video memory access (BIOS interrupts)
- **DOSBox** emulates this, but timing/synchronization can be tricky
- Display swapping requires:
  - Saving video RAM (4000 bytes for text mode)
  - Switching video modes (INT 10h)
  - Restoring on return
- DOSBox might not flush these changes to the window immediately

### From Turbo C++ README
> "When debugging a mouse application the Options|Debugger|Display  
> Swapping option should be set to 'Always' for best results.  
>  
> In the IDE, the mouse cursor is turned off during compilation  
> for performance improvements."

### DOSBox Emulation Limits
- Not a perfect DOS replica
- Video timing approximations
- Some programs need specific configurations

## Still Not Working?

1. **Check DPMI**:
   ```dos
   C:\> TC\BIN\DPMIINST
   ```
   Follow prompts to add your machine to DPMI database.

2. **Try real-mode compiler** (if available):
   - Turbo C++ 3.0 uses protected-mode (DPMI)
   - Some older versions had real-mode compilers
   - More compatible with DOSBox

3. **Use external console**:
   - Some DOSBox builds support `-noconsole` flag
   - Opens separate window for program output

4. **Report issue**:
   - Check: https://github.com/amitdevx/TurboCPP/issues
   - Include: DOSBox version, OS, `dosbox-turbo.conf` settings

## Quick Reference Card

| Key         | Action               | When to Use                      |
|-------------|----------------------|----------------------------------|
| Ctrl+F9     | Compile & Run        | Test program (after fix applied) |
| Alt+F9      | Compile Only         | Just compile, run manually later |
| F9          | Make                 | Build project                    |
| Ctrl+F2     | Stop Program         | Kill running/hung program        |
| Alt+F5      | User Screen          | See last program output          |
| Alt+X       | Exit TC++            | Return to DOS                    |

**Alt+F5 (User Screen)** is especially useful - it shows the last output from your program even after it finished!

---

**TL;DR**: Set Options → Debugger → Display Swapping → **Always**, then save. Problem should be fixed!
