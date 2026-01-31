# Windows Task Scheduler Setup for Stock Scraper
# This script sets up automatic scheduling so the scraper runs at market open
# Run this in PowerShell as Administrator

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Stock Scraper - Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verify running as Administrator
$isAdmin = [Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains 'S-1-5-32-544'
if (-not $isAdmin) {
    Write-Host "ERROR: This script must run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Red
    pause
    exit
}

# Configuration
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$batFile = Join-Path $scriptPath "run_scraper.bat"
$pythonScript = Join-Path $scriptPath "scraper.py"
$taskName = "StockScreener_DataCollection"
$taskDescription = "Automated stock data collection - Runs every morning at 9:15 AM IST (11:45 PM UTC)"

# Verify files exist
if (-not (Test-Path $batFile)) {
    Write-Host "ERROR: run_scraper.bat not found at $batFile" -ForegroundColor Red
    pause
    exit
}

if (-not (Test-Path $pythonScript)) {
    Write-Host "ERROR: scraper.py not found at $pythonScript" -ForegroundColor Red
    pause
    exit
}

Write-Host "✓ Script files found" -ForegroundColor Green
Write-Host "  - Batch: $batFile" -ForegroundColor Gray
Write-Host "  - Python: $pythonScript" -ForegroundColor Gray
Write-Host ""

# Remove existing task if it exists
Write-Host "Checking for existing task..." -ForegroundColor Yellow
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Found existing task. Removing..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "✓ Old task removed" -ForegroundColor Green
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "Creating new scheduled task..." -ForegroundColor Yellow

try {
    # Create trigger - Daily at 9:15 AM (Market open in India)
    $trigger = New-ScheduledTaskTrigger -Daily -At 9:15AM
    
    # Create action
    $action = New-ScheduledTaskAction -Execute $batFile -WorkingDirectory $scriptPath
    
    # Create settings (allow parallel runs, restart on failure)
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5) -MultipleInstancePolicy Queue
    
    # Create the task
    Register-ScheduledTask -TaskName $taskName -Description $taskDescription -Trigger $trigger -Action $action -Settings $settings -Force | Out-Null
    
    Write-Host "✓ Task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $taskName" -ForegroundColor Gray
    Write-Host "  Schedule: Daily at 9:15 AM" -ForegroundColor Gray
    Write-Host "  Auto-restart: Yes (on failure)" -ForegroundColor Gray
    Write-Host "  Batch File: $batFile" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "ERROR: Failed to create task" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    pause
    exit
}

# Optional: Create additional trigger for task restart
Write-Host ""
Write-Host "Configuration Options:" -ForegroundColor Yellow
Write-Host "1. Run immediately (for testing)" -ForegroundColor Cyan
Write-Host "2. View task in Task Scheduler" -ForegroundColor Cyan
Write-Host "3. Exit" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Select option (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Running scraper immediately..." -ForegroundColor Yellow
        & $batFile
    }
    "2" {
        Write-Host ""
        Write-Host "Opening Task Scheduler..." -ForegroundColor Yellow
        Start-Process taskmgr.exe
    }
    "3" {
        Write-Host ""
        Write-Host "Setup complete!" -ForegroundColor Green
    }
    default {
        Write-Host ""
        Write-Host "Setup complete!" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Status: Ready for automated operation" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Verify database connection in .env file" -ForegroundColor Gray
Write-Host "2. Test the scraper manually: python scraper.py" -ForegroundColor Gray
Write-Host "3. Check logs directory for execution logs" -ForegroundColor Gray
Write-Host "4. Task will auto-run at 9:15 AM tomorrow" -ForegroundColor Gray
Write-Host ""
