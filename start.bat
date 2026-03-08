@echo off
title TurboCPP for Windows (via DOSBox)

echo +---------------------------------------------------------------+
echo ^|                                                               ^|
echo ^|    _____  _   _  ____   ____    ___     ____  ____   ____     ^|
echo ^|   ^|_   _^|^| ^| ^| ^|^|  _ \ ^| __ )  / _ \   / ___^|^|  _ \ ^|  _ \    ^|
echo ^|     ^| ^|  ^| ^| ^| ^|^| ^|_) ^|+  _ \ ^| ^| ^| ^| ^| ^|    ^| ^|_) ^|+ ^|_) ^|   ^|
echo ^|     ^| ^|  ^| ^|_^| ^|+  _ ^< ^| ^|_) ^|^| ^|_^| ^| ^| ^|___ ^|  __/ ^|  __/    ^|
echo ^|     ^|_^|   \___/ ^|_^| \_\^|____/  \___/   \____^|^|_^|    ^|_^|       ^|
echo ^|                                                               ^|
echo ^|         TurboCPP for Windows via DOSBox Emulator              ^|
echo ^|                                                               ^|
echo +---------------------------------------------------------------+
echo.

REM Check if DOSBox is on PATH
where dosbox >nul 2>nul
if %errorlevel% neq 0 (
    echo DOSBox not found on PATH.
    echo Checking common install locations...

    if exist "C:\Program Files (x86)\DOSBox-0.74-3\dosbox.exe" (
        set "DOSBOX=C:\Program Files (x86)\DOSBox-0.74-3\dosbox.exe"
        goto :found
    )
    if exist "C:\Program Files\DOSBox-0.74-3\dosbox.exe" (
        set "DOSBOX=C:\Program Files\DOSBox-0.74-3\dosbox.exe"
        goto :found
    )
    if exist "C:\Program Files (x86)\DOSBox-0.74\dosbox.exe" (
        set "DOSBOX=C:\Program Files (x86)\DOSBox-0.74\dosbox.exe"
        goto :found
    )

    echo.
    echo ERROR: DOSBox is not installed or not found.
    echo Please install DOSBox from https://www.dosbox.com/download.php
    echo Then re-run this script.
    pause
    exit /b 1
) else (
    set "DOSBOX=dosbox"
)

:found
echo Starting Turbo C++ ...
echo.

REM ─── TurboCPP AI: Start AI watcher in background ───────────────
set "AI_STARTED=0"
if exist "%~dp0ai\main.py" (
    REM Try python then python3
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set "PYTHON=python"
    ) else (
        where python3 >nul 2>nul
        if %errorlevel% equ 0 (
            set "PYTHON=python3"
        )
    )
)

if defined PYTHON (
    if exist "%~dp0ai\config.json" (
        REM Check if API key is configured
        %PYTHON% -c "import json,sys;cfg=json.load(open(r'%~dp0ai\config.json'));sys.exit(0 if cfg.get('openrouter_api_key','') else 1)" 2>nul
        if %errorlevel% equ 0 (
            echo   [AI] TurboCPP AI: Starting AI code assistant...
            echo   [AI] Write '@ai ^<prompt^>' in any .c/.cpp file to generate code!
            echo.
            if not exist "%~dp0ai\logs" mkdir "%~dp0ai\logs"
            start /B "" %PYTHON% "%~dp0ai\main.py" watch "%~dp0." > "%~dp0ai\logs\watcher.log" 2>&1
            set "AI_STARTED=1"
            echo   [AI] AI watcher running in background.
            echo.
        ) else (
            echo   [AI] TurboCPP AI available but not configured.
            echo   Run: %PYTHON% ai\main.py setup
            echo.
        )
    ) else (
        echo   [AI] TurboCPP AI available but not configured.
        echo   Run: %PYTHON% ai\main.py setup
        echo.
    )
)
REM ────────────────────────────────────────────────────────────────

REM Use project-local config if it exists
set "CONF="
if exist "%~dp0dosbox-turbo.conf" (
    set "CONF=-conf "%~dp0dosbox-turbo.conf""
)

"%DOSBOX%" %CONF% -c "mount C \"%~dp0.\"" -c "SET PATH=%%PATH%%;C:\TURBOC3\BIN" -c "C:" -c "CD TURBOC3\BIN" -c "TC"

REM ─── Cleanup: Stop AI watcher when DOSBox exits ────────────────
if "%AI_STARTED%"=="1" (
    echo   Stopping AI watcher...
    REM Kill any python watcher processes started by this script
    taskkill /F /FI "WINDOWTITLE eq TurboCPP*" >nul 2>nul
    REM Also kill by command line pattern
    for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST 2^>nul ^| findstr "PID"') do (
        wmic process where "ProcessId=%%a and CommandLine like '%%ai\\main.py%%watch%%'" call terminate >nul 2>nul
    )
    echo   AI watcher stopped.
)
echo.
echo Turbo C++ session ended.

