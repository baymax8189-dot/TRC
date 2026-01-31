# Zero-Touch Automation Setup Guide

**Goal:** Complete automatic data collection with no manual intervention

## ✅ What's Automated

- **Data Pulling**: Every 1 minute during market hours (9:15 AM - 3:30 PM IST)
- **Error Recovery**: Auto-retry 3 times if pull fails, then refresh and continue
- **Page Refresh**: Automatic between each pull
- **Task Scheduling**: Auto-start at 9:15 AM via Windows Task Scheduler
- **Auto-Restart**: Restarts on crashes with intelligent recovery

---

## 🚀 Step 1: Initial Environment Setup

### Prerequisites
- ✅ Python 3.9+ installed
- ✅ Chrome browser installed
- ✅ ChromeDriver matching your Chrome version
- ✅ Windows PowerShell (as Administrator)

### Check Python Installation
```powershell
python --version
pip --version
```

### Install Required Packages
From the `selenium/` directory:
```powershell
pip install -r requirements.txt
```

---

## 🔧 Step 2: Configure Environment Variables

Create `.env` in the `selenium/` directory:
```env
# Backend API Configuration
API_URL=https://your-backend-url.onrender.com
# Example: API_URL=https://stock-screener-api.onrender.com

# Download Directory (auto-created if doesn't exist)
DOWNLOAD_PATH=./downloads
```

### Verify Environment
Test the connection to your API:
```powershell
$env:API_URL = "https://your-backend-url.onrender.com"
python -c "import os; print(os.getenv('API_URL'))"
```

---

## ✨ Step 3: Automatic Scheduling (Windows Task Scheduler)

### Method A: PowerShell Setup (Recommended)

1. **Open PowerShell as Administrator**
   - Right-click PowerShell
   - Select "Run as Administrator"

2. **Run Setup Script**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   & "C:\path\to\selenium\setup_scheduler.ps1"
   ```

3. **Follow the prompts**
   - Script will create the scheduled task
   - Choose to run immediately for testing (recommended)
   - View logs in `selenium/logs/` directory

### Method B: Manual Task Scheduler Setup

1. **Open Task Scheduler**
   - Press `Win + R`
   - Type `taskschd.msc`
   - Click OK

2. **Create Basic Task**
   - Right-click "Task Scheduler Library"
   - Select "Create Basic Task..."
   - Name: `StockScreener_DataCollection`
   - Description: "Automated stock data collection"

3. **Set Trigger**
   - Trigger Type: "Daily"
   - Start Time: `09:15 AM`
   - Advanced Settings: "Repeat every 1 day"

4. **Set Action**
   - Program: `C:\path\to\selenium\run_scraper.bat`
   - Start in: `C:\path\to\selenium\`

5. **Set Conditions**
   - Check: "Start the task only if the computer is on AC power"
   - Check: "Wake the computer to run this task" (optional)

6. **Set Settings**
   - Check: "If the task fails, restart every 5 minutes"
   - Check: "Stop the task if it runs longer than 12 hours"
   - Check: "Allow task to be run on demand"

---

## 📊 Step 4: Monitor Execution

### View Logs
```powershell
# Real-time log viewing
Get-Content -Path "C:\path\to\selenium\logs\scraper_auto_*.log" -Wait

# Check latest scrape success
Get-ChildItem -Path "C:\path\to\selenium\logs\" -Recurse | 
  Select-Object -Last 1 | 
  Get-Content
```

### Check Task Status
```powershell
# List scheduled tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "*StockScreener*"} | 
  Select-Object TaskName, State, LastRunTime, NextRunTime

# View task history
Get-ScheduledTaskInfo -TaskName "StockScreener_DataCollection"
```

### Monitor API Connectivity
```powershell
# Test API endpoint
$API_URL = "https://your-backend-url.onrender.com"
Invoke-RestMethod -Uri "$API_URL/health" -Method Get
```

---

## 🔄 Step 5: Error Recovery & Troubleshooting

### Auto-Recovery Features Built-In

1. **Network Failure**
   - Retries 3 times with 5-second delays
   - Refreshes page and tries again
   - Logs all failures

2. **Browser Crash**
   - Batch file detects exit code
   - Auto-restarts browser
   - Maximum 5 crashes allowed per session

3. **Download Timeout**
   - Waits up to 10 seconds for CSV
   - On timeout, refreshes and retries

4. **API Connection Issues**
   - Retries with exponential backoff
   - Falls through to next 1-minute cycle
   - Logs error for debugging

### Manual Recovery

**If scraper stops:**
```powershell
# View recent log
Get-Content "C:\path\to\selenium\logs\scraper_auto_*.log" -Tail 50

# Manual restart
& "C:\path\to\selenium\run_scraper.bat"
```

**If database is down:**
- Scraper continues running (offline mode)
- Buffers data in memory
- Resends when connection restored

**If Chrome crashes repeatedly:**
- Check `selenium/logs/` for error details
- Verify Chrome version: `chrome://version/`
- Update ChromeDriver matching version
- Restart Windows Task Scheduler task

---

## 🧪 Step 6: Testing

### Test 1: Manual Scraper Execution
```powershell
cd C:\path\to\selenium
python scraper.py
```
Expected: Pulls data, logs to console, waits 60 seconds, repeats

### Test 2: Batch File Execution
```powershell
cd C:\path\to\selenium
.\run_scraper.bat
```
Expected: Shows colored output, creates logs directory, starts scraper with auto-restart capability

### Test 3: Verify Task Scheduling
```powershell
# Trigger task immediately
Start-ScheduledTask -TaskName "StockScreener_DataCollection"

# Wait 30 seconds
Start-Sleep -Seconds 30

# Check if running
Get-Process chrome | Where-Object {$_.ProcessName -eq "chrome"}
```

---

## 📈 Performance Monitoring

### Database Growth
```sql
-- Check current data volume
SELECT COUNT(*) as total_records, 
       MIN(timestamp) as earliest,
       MAX(timestamp) as latest
FROM stocks;

-- Check data ingestion rate
SELECT DATE_TRUNC('minute', timestamp) as minute,
       COUNT(*) as records_per_minute
FROM stocks
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY 1
ORDER BY 1 DESC;
```

### API Response Times
- Dashboard fetches: ~50-80ms (cached)
- Analytics queries: ~100-150ms (aggregated)
- Data insertion: ~20-40ms (bulk operations)

### System Resources
- Memory: ~300-400 MB (Chrome + Python)
- CPU: ~2-5% idle, 15-20% during pulls
- Network: ~100-200 KB per pull

---

## 🛡️ Troubleshooting Matrix

| Issue | Symptom | Solution |
|-------|---------|----------|
| No data appearing | Dashboard empty | Check API health, verify database connection |
| Task not running | Logs not updating | Verify Task Scheduler is enabled, check permissions |
| Chrome crashes | Frequent restarts | Update Chrome, verify ChromeDriver version match |
| API timeouts | Retries in logs | Check backend service health (Render status) |
| Download fails | CSV not found in logs | Verify website hasn't changed layout |
| Task disabled | Schedule shows "Disabled" | Right-click task → Enable |

---

## 🔐 Security Notes

- ✅ Credentials stored in `.env` (never commit to git)
- ✅ API URL should be HTTPS only
- ✅ Database connection uses SSL
- ✅ Logs contain no sensitive data
- ✅ Chrome runs in headless mode (no window shown)

---

## 📞 Support Resources

### Check Logs
```
C:\path\to\selenium\logs\scraper_auto_YYYYMMDD_HHMM.log
```

### API Health Check
```
GET https://your-api.onrender.com/health
```

### Database Status
```
SELECT NOW() as server_time, COUNT(*) as total_records FROM stocks;
```

### Browser Compatibility
- Chrome 90+
- ChromeDriver matching version
- Windows 10/11

---

## 📋 Checklist Before Going Live

- [ ] Python installed and working (`python --version`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with correct API_URL
- [ ] API endpoint is reachable (`curl https://api-url/health`)
- [ ] Database is accessible and tested
- [ ] Manual test passed (`python scraper.py` runs for 5+ minutes)
- [ ] Batch file works (`run_scraper.bat` shows proper output)
- [ ] Task Scheduler configured (`setup_scheduler.ps1` completed)
- [ ] Logs directory exists and is writable
- [ ] Chrome and ChromeDriver versions match
- [ ] Dashboard displays incoming data (wait 5-10 minutes)

---

## ✅ You're Now Zero-Touch!

Once everything is set up:
1. **Task Scheduler runs at 9:15 AM daily**
2. **Scraper auto-restarts on failure**
3. **Data flows automatically to dashboard**
4. **No manual intervention needed**
5. **Logs track all activity for debugging**

Your stock screener is now fully automated! 🚀
