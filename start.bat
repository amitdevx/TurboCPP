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

REM Use project-local config if it exists
set "CONF="
if exist "%~dp0dosbox-turbo.conf" (
    set "CONF=-conf "%~dp0dosbox-turbo.conf""
)

"%DOSBOX%" %CONF% -c "mount C \"%~dp0.\"" -c "SET PATH=%%PATH%%;C:\TC\BIN" -c "C:" -c "TC"
