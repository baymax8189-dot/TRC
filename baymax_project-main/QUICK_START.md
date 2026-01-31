# ⚡ Quick Start: Zero-Touch Automation

**TL;DR** - Get your scraper running automatically in 5 minutes.

## What You Need
- Windows 10/11
- Python 3.9+ 
- Chrome browser
- 5 minutes

## Step 1: Install Dependencies (2 minutes)
```powershell
cd selenium
pip install -r requirements.txt
```

## Step 2: Configure API (1 minute)
Edit `selenium/.env`:
```env
API_URL=https://your-backend-url.onrender.com
```

## Step 3: Set Up Automatic Scheduling (2 minutes)

**Open PowerShell as Administrator**, then:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
cd C:\path\to\selenium
.\setup_scheduler.ps1
```

Done! ✅

---

## What Happens Now

| Time | What Runs | Details |
|------|-----------|---------|
| 9:15 AM | Scraper starts | Windows Task Scheduler triggers |
| 9:15 AM+ | Data pulls every 1 min | Extracts CSV, sends to API |
| 3:30 PM | Scraper pauses | Market hours end, waits for next day |
| Crashes | Auto-restart | Retries 3x, then refreshes page |

## Monitor It

**Check if running:**
```powershell
Get-Content "selenium/logs/scraper_auto_*.log" -Tail 20
```

**Manual start (for testing):**
```powershell
.\run_scraper.bat
```

**View dashboard:**
```
https://your-vercel-frontend.vercel.app
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No data in dashboard | Check `.env` API_URL is correct |
| Logs show API errors | Verify backend is running on Render |
| Chrome crashes frequently | Update ChromeDriver to match Chrome version |
| Task never runs | Check Task Scheduler is enabled: `schtasks /query /tn StockScreener*` |

---

## Full Documentation

See [ZERO_TOUCH_SETUP.md](ZERO_TOUCH_SETUP.md) for detailed guide.

## Check System Health

```powershell
python health_monitor.py
```

Shows:
- ✓ API status
- ✓ Database health
- ✓ Latest data age
- ✓ Scraper activity

---

**That's it! Your stock screener is now fully automated.** 🚀

No more manual work needed - it all happens automatically every morning!
