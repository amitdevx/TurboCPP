# Debugging Ctrl+F9 Issue in TurboCPP

## User Report
- Ctrl+F9 (Compile & Run) quits immediately
- Happens even with simple programs (printf + getch)
- Issue is NOT in AI code generation
- Issue is in the CORE APPLICATION (DOSBox/Turbo C++ setup)

## What Ctrl+F9 Does
In Turbo C++ IDE:
1. Compiles the current file
2. Links it to create .EXE
3. Runs the .EXE in a DOS window
4. Should wait for program to finish
5. Return to IDE

## Potential Root Causes

### 1. Display Swapping Issue (from TC README line 308-311)
```
"When debugging a mouse application the Options|Debugger|Display
Swapping option should be set to "Always" for best results.

In the IDE, the mouse cursor is turned off during compilation
for performance improvements."
```

**HYPOTHESIS**: DOSBox might not be swapping displays properly when running programs from IDE.

### 2. DOSBox Window Configuration
- `output=surface` in dosbox-turbo.conf (line 10)
- Could cause issues with program output display
- Programs might run but output goes to wrong buffer

### 3. Missing DPMI Configuration
- TC.EXE requires DPMI (see README lines 188-223)
- DPMIINST might need to be run for this machine
- README says: "If you encounter a 'machine not in database' message while attempting to run the compiler, run the DPMIINST program"

### 4. DOSBox Cycles Too Low
- Current: `cycles=3000` (line 32)
- Might be too slow for program execution
- Program might timeout or get killed

### 5. Screen/Console Buffer Issue
- Turbo C++ might be writing to wrong video memory
- DOSBox might not be capturing the output
- getch() might not be waiting for input properly

## Testing Strategy

1. **Test outside IDE**: Compile manually with TCC.EXE, run .EXE directly
2. **Test DOSBox display**: Check if programs run but output is invisible
3. **Check DPMI**: Run DPMIINST.EXE in DOSBox
4. **Try different cycles**: Increase to 8000-10000
5. **Test display swapping**: Check IDE debugger options

## Next Steps
1. Boot DOSBox manually
2. Compile test_simple.c with TCC.EXE
3. Run test_simple.exe directly
4. Check if output appears
5. If works: IDE config issue
6. If fails: DOSBox/DPMI issue
