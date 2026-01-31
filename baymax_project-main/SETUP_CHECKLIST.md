# 🎯 Your Next Steps - Zero-Touch Automation

**You're ready to go live!** Follow these steps in order.

---

## ✅ Phase 1: Verify Environment (5 minutes)

- [ ] **Check Python Installation**
  ```powershell
  python --version
  ```
  Expected: Python 3.9 or higher

- [ ] **Check Chrome Installation**
  - Open Chrome browser
  - Go to: `chrome://version/`
  - Note the version number (e.g., 120.0.6099.129)

- [ ] **Download Correct ChromeDriver**
  - Visit: https://chromedriver.chromium.org/downloads
  - Download version matching your Chrome version
  - Extract to: `selenium/` folder

- [ ] **Install Python Dependencies**
  ```powershell
  cd selenium
  pip install -r requirements.txt
  ```

---

## ✅ Phase 2: Configure Environment (2 minutes)

- [ ] **Update `.env` File**
  - Open: `selenium/.env`
  - Set your API URL:
    ```env
    API_URL=https://your-backend-on-render.onrender.com
    DOWNLOAD_PATH=./downloads
    ```
  - Save the file

- [ ] **Verify API Connectivity**
  ```powershell
  $API_URL = "https://your-backend-on-render.onrender.com"
  Invoke-RestMethod -Uri "$API_URL/health" -Method Get
  ```
  Expected: Response with status info

---

## ✅ Phase 3: Manual Test (3 minutes)

- [ ] **Test Scraper Manually**
  ```powershell
  cd selenium
  python scraper.py
  ```
  
- [ ] **Verify Output**
  - Should download CSV
  - Should log: "✓ CSV clicked"
  - Should log: "✓ API Success"
  - Should wait 60 seconds
  - Should repeat

- [ ] **Check Dashboard**
  - Open frontend: `https://your-vercel-frontend.vercel.app`
  - Wait 5-10 minutes
  - Should show data appearing
  - Should show timestamps updating

- [ ] **Stop the Test**
  - Press `Ctrl+C` in terminal
  - Browser should close

---

## ✅ Phase 4: Set Up Automatic Scheduling (5 minutes)

### **IMPORTANT: Run PowerShell as Administrator!**

- [ ] **Open PowerShell as Administrator**
  - Right-click on PowerShell
  - Select "Run as Administrator"

- [ ] **Navigate to Selenium Folder**
  ```powershell
  cd C:\full\path\to\chartlink-app\selenium
  ```

- [ ] **Set Execution Policy**
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
  - Type: `Y` and press Enter

- [ ] **Run Setup Script**
  ```powershell
  .\setup_scheduler.ps1
  ```
  
- [ ] **Follow Prompts**
  - Script should create the scheduled task
  - When asked, select option `1` to run immediately (for testing)
  - Monitor the output

- [ ] **Verify Task Creation**
  ```powershell
  Get-ScheduledTask -TaskName "StockScreener_DataCollection" | Select-Object TaskName, State, NextRunTime
  ```
  Expected: Task shows "Ready" state and tomorrow's 9:15 AM NextRunTime

---

## ✅ Phase 5: Verify Everything Works (5 minutes)

- [ ] **Check Logs Folder**
  - Navigate to: `selenium/logs/`
  - Should see files like: `scraper_auto_20240115_0915.log`

- [ ] **View Recent Logs**
  ```powershell
  Get-Content "selenium\logs\scraper_auto_*.log" -Tail 30
  ```
  Should show successful data pulls

- [ ] **Run Health Monitor**
  ```powershell
  python selenium\health_monitor.py
  ```
  Expected: All components show HEALTHY status

- [ ] **Check Dashboard One More Time**
  - Refresh: `https://your-vercel-frontend.vercel.app`
  - Should show latest data
  - Should show timestamp from last 5 minutes

---

## ✅ Phase 6: Monitor Tomorrow (Optional but Recommended)

**Tomorrow at 9:15 AM:**

- [ ] **Verify Scraper Started Automatically**
  ```powershell
  # Check if Chrome process exists
  Get-Process chrome | Where-Object {$_.ProcessName -eq "chrome"}
  
  # View latest logs
  Get-Content "selenium\logs\scraper_auto_*.log" -Tail 20
  ```

- [ ] **Check Dashboard Updates**
  - Refresh: `https://your-vercel-frontend.vercel.app`
  - Data should be updating every 5 minutes
  - Timestamp should be current

- [ ] **Set Up Optional Monitoring**
  ```powershell
  # Run health check daily
  # Add to your own task scheduler if desired
  python selenium\health_monitor.py
  ```

---

## 🚨 Troubleshooting During Setup

### Issue: Python Not Found
```
Error: 'python' is not recognized
```
**Fix:**
- Install Python from https://www.python.org/downloads/
- Check "Add Python to PATH" during installation
- Restart PowerShell

### Issue: Permission Denied
```
Error: Access is denied
```
**Fix:**
- Run PowerShell as Administrator
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Issue: Chrome Not Found
```
Error: Chrome executable not found
```
**Fix:**
- Install Chrome from https://www.google.com/chrome/
- Verify path in scraper.py (line with `webdriver.Chrome`)

### Issue: API Connection Failed
```
Error: Failed to connect to API_URL
```
**Fix:**
- Verify API_URL in `.env` file (should start with `https://`)
- Check backend is running on Render
- Visit `https://your-api.onrender.com/health` in browser

### Issue: Task Scheduled but Not Running
```
Task shows in scheduler but no activity
```
**Fix:**
- Right-click task in Task Scheduler
- Select "Enable"
- Select "Run" to test immediately
- Check logs for errors

---

## 📊 After Setup - What to Expect

### First Day
- ✅ Scraper runs at 9:15 AM
- ✅ Dashboard shows data appearing
- ✅ Data refreshes every 5 minutes
- ✅ 50+ stock records per minute ingested

### First Week
- ✅ Dashboard shows trends
- ✅ Analytics become more accurate
- ✅ Top gainers/losers update in real-time
- ✅ Zero manual intervention needed

### First Month
- ✅ Database has ~600K records
- ✅ Historical trends visible
- ✅ Full automation validated
- ✅ Monitoring logs confirm reliability

---

## 📞 Quick Help

| Problem | Command | Expected Result |
|---------|---------|-----------------|
| Check if running | `Get-Process chrome` | Shows chrome.exe processes |
| View logs | `Get-Content "selenium\logs\scraper_auto_*.log" -Tail 20` | Shows recent activity |
| Manual start | `.\run_scraper.bat` | Batch file runs with colored output |
| Health check | `python selenium\health_monitor.py` | Shows all components HEALTHY |
| API test | `Invoke-RestMethod -Uri "https://your-api/health"` | Returns status info |

---

## 🎉 You're Done!

Your system is now **fully automated and ready for production.**

**What happens automatically now:**
- ✅ Runs every weekday morning at 9:15 AM
- ✅ Pulls data every minute during market hours
- ✅ Restarts automatically on failures
- ✅ Dashboard updates every 5 minutes
- ✅ Zero manual intervention needed

**No more work needed!** Just let it run. 🚀

---

## 📚 Additional Resources

- **Full Setup Guide**: [ZERO_TOUCH_SETUP.md](ZERO_TOUCH_SETUP.md)
- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **Completion Report**: [COMPLETION_REPORT.md](COMPLETION_REPORT.md)
- **Logs**: `selenium/logs/` directory

---

**Questions?** Check the troubleshooting section or review logs:
```powershell
Get-Content "selenium\logs\scraper_auto_*.log" -Tail 50
