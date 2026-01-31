@echo off
REM Run Selenium Scraper with Auto-Restart on Failure
REM This batch file runs the scraper in a loop with auto-recovery

setlocal enabledelayedexpansion

REM Configuration
set PYTHON_PATH=python
set SCRIPT_PATH=%~dp0scraper.py
set LOG_DIR=%~dp0logs
set MAX_CRASHES=5
set CRASH_WINDOW=3600
set RESTART_DELAY=5

REM Create logs directory if it doesn't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Get timestamp for log file
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set LOGFILE=%LOG_DIR%\scraper_auto_%mydate%_%mytime%.log

echo.
echo ========================================
echo Selenium Stock Scraper Auto-Restart
echo ========================================
echo Log File: %LOGFILE%
echo Start Time: %date% %time%
echo.

REM Check if Python is installed
%PYTHON_PATH% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python and add it to PATH.
    echo Visit: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if script exists
if not exist "%SCRIPT_PATH%" (
    echo ERROR: Script not found: %SCRIPT_PATH%
    pause
    exit /b 1
)

REM Main loop with crash recovery
set CRASH_COUNT=0
set FIRST_CRASH_TIME=0

:LOOP
set CRASH_COUNT=!CRASH_COUNT!+1
set /a CRASH_COUNT=!CRASH_COUNT!

echo [%date% %time%] Starting scraper (Attempt !CRASH_COUNT!)... >> "%LOGFILE%"
echo Starting scraper (Attempt !CRASH_COUNT!)...

REM Run the Python script
%PYTHON_PATH% "%SCRIPT_PATH%" >> "%LOGFILE%" 2>&1

REM Check exit code
set EXIT_CODE=!ERRORLEVEL!

echo [%date% %time%] Scraper exited with code !EXIT_CODE! >> "%LOGFILE%"

if !EXIT_CODE! equ 0 (
    echo [%date% %time%] Normal exit detected >> "%LOGFILE%"
    set CRASH_COUNT=0
    set FIRST_CRASH_TIME=0
) else (
    echo Scraper crashed! Exit code: !EXIT_CODE!
    
    if !CRASH_COUNT! geq %MAX_CRASHES% (
        echo [%date% %time%] CRITICAL: Too many crashes (!CRASH_COUNT!/!MAX_CRASHES!). Stopping. >> "%LOGFILE%"
        echo CRITICAL: Too many crashes. Please check logs and environment.
        echo Log: %LOGFILE%
        pause
        exit /b 1
    )
    
    echo [%date% %time%] Crash #!CRASH_COUNT! - Restarting in %RESTART_DELAY% seconds >> "%LOGFILE%"
    echo Restarting in %RESTART_DELAY% seconds...
    timeout /t %RESTART_DELAY% /nobreak
)

goto LOOP

endlocal
