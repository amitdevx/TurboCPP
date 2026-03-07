@echo off
REM ================================================================
REM  TurboCPP AI — One-Click Setup for Windows
REM  Installs all dependencies and configures AI code generation.
REM ================================================================

title TurboCPP AI Setup

echo.
echo ========================================================
echo     TurboCPP AI Setup — One-Click Installer (Windows)
echo ========================================================
echo.

set "PROJECT_DIR=%~dp0"
set "ERRORS=0"
set "PYTHON="

REM ─── Step 1: Check DOSBox ──────────────────────────────────────
echo [1/4] Checking DOSBox...
where dosbox >nul 2>nul
if %errorlevel% equ 0 (
    echo   [OK] DOSBox found on PATH.
    goto :dosbox_done
)

if exist "C:\Program Files (x86)\DOSBox-0.74-3\dosbox.exe" (
    echo   [OK] DOSBox found at C:\Program Files (x86)\DOSBox-0.74-3\
    goto :dosbox_done
)
if exist "C:\Program Files\DOSBox-0.74-3\dosbox.exe" (
    echo   [OK] DOSBox found at C:\Program Files\DOSBox-0.74-3\
    goto :dosbox_done
)
if exist "C:\Program Files (x86)\DOSBox-0.74\dosbox.exe" (
    echo   [OK] DOSBox found at C:\Program Files (x86)\DOSBox-0.74\
    goto :dosbox_done
)

echo   [!!] DOSBox not found!
echo   Please download and install DOSBox from:
echo     https://www.dosbox.com/download.php
echo   After installing, re-run this setup.
set /a ERRORS+=1

:dosbox_done
echo.

REM ─── Step 2: Check Python ──────────────────────────────────────
echo [2/4] Checking Python 3...

REM Try "python" first (Windows default), then "python3"
where python >nul 2>nul
if %errorlevel% equ 0 (
    python --version 2>&1 | findstr /R "^Python 3\." >nul
    if %errorlevel% equ 0 (
        set "PYTHON=python"
        echo   [OK] Python found.
        goto :python_done
    )
)

where python3 >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON=python3"
    echo   [OK] Python3 found.
    goto :python_done
)

REM Check Windows Store alias / py launcher
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -3 --version >nul 2>nul
    if %errorlevel% equ 0 (
        set "PYTHON=py -3"
        echo   [OK] Python found via py launcher.
        goto :python_done
    )
)

echo   [!!] Python 3 not found!
echo   Please install Python 3.8+ from:
echo     https://www.python.org/downloads/
echo   IMPORTANT: Check "Add Python to PATH" during installation!
echo.
echo   Opening Python download page...
start https://www.python.org/downloads/
set /a ERRORS+=1
goto :python_done

:python_done
echo.

REM ─── Step 3: Install Python packages ───────────────────────────
echo [3/4] Installing Python packages...
if not defined PYTHON (
    echo   [SKIP] Python not available.
    set /a ERRORS+=1
    goto :pip_done
)

%PYTHON% -m pip install -q -r "%PROJECT_DIR%ai\requirements.txt" 2>&1
if %errorlevel% neq 0 (
    echo   [!!] pip install failed. Trying with --user flag...
    %PYTHON% -m pip install --user -q -r "%PROJECT_DIR%ai\requirements.txt" 2>&1
)

REM Verify packages installed
%PYTHON% -c "import watchdog, requests" 2>nul
if %errorlevel% equ 0 (
    echo   [OK] watchdog and requests installed.
) else (
    echo   [!!] Package install failed.
    echo   Try manually: %PYTHON% -m pip install watchdog requests
    set /a ERRORS+=1
)

:pip_done
echo.

REM ─── Step 4: Create AI config and directories ─────────────────
echo [4/4] Setting up AI configuration...

if not exist "%PROJECT_DIR%ai\logs" mkdir "%PROJECT_DIR%ai\logs"
if not exist "%PROJECT_DIR%ai\backups" mkdir "%PROJECT_DIR%ai\backups"

if not exist "%PROJECT_DIR%ai\config.json" (
    if exist "%PROJECT_DIR%ai\config.example.json" (
        copy /Y "%PROJECT_DIR%ai\config.example.json" "%PROJECT_DIR%ai\config.json" >nul
        echo   [OK] Config created from template.
    )
) else (
    echo   [OK] Config already exists.
)
echo.

REM ─── Summary ───────────────────────────────────────────────────
echo ========================================================
if %ERRORS% equ 0 (
    echo   Setup complete! All dependencies installed.
) else (
    echo   Setup finished with %ERRORS% issue(s). See above.
)
echo ========================================================
echo.
echo Next steps:
echo   1. Get your FREE API key from: https://openrouter.ai/keys
if defined PYTHON (
    echo   2. Run the AI setup wizard: %PYTHON% ai\main.py setup
    echo   3. Start TurboCPP with AI:  start.bat
) else (
    echo   2. Install Python 3.8+ first, then re-run setup.bat
)
echo.
pause
