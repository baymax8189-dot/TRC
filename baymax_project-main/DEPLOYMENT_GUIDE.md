# 🚀 STEP-BY-STEP DEPLOYMENT GUIDE

## Phase 1: Database Setup (5 minutes)

### Step 1.1: Create Neon Account
```
1. Go to https://neon.tech
2. Click "Sign up"
3. Sign in with GitHub (recommended)
4. Click "Create new project"
5. Name: chartlink
6. Region: US East (or your region)
7. Click "Create project"
```

### Step 1.2: Get Connection String
```
1. Project created → Dashboard shows
2. Copy connection string (looks like):
   postgresql://user:password@ep-xyz.neon.tech/chartlink
3. Keep this safe - you'll need it for backend
```

### Step 1.3: Save to Backend
```
1. Open: backend/.env
2. Replace DATABASE_URL=... with your connection string
3. Save file
4. Example:
   DATABASE_URL=postgresql://user123:pass456@ep-abc123.neon.tech/chartlink
```

✅ **Database ready!**

---

## Phase 2: Deploy Backend (10 minutes)

### Step 2.1: Prepare GitHub
```
1. Go to https://github.com
2. Create new repository: "chartlink-backend"
3. Description: "Stock screener API with analytics"
4. Make it PUBLIC
5. Don't add README/gitignore (we have .gitignore)
6. Click "Create repository"
```

### Step 2.2: Push Backend to GitHub
```bash
cd backend

# Initialize git
git init
git add .
git commit -m "Initial backend with analytics layer"

# Connect to GitHub
git remote add origin https://github.com/YOUR_USERNAME/chartlink-backend.git
git branch -M main
git push -u origin main

# You should see: ✓ Done (all files pushed)
```

### Step 2.3: Deploy to Render
```
1. Go to https://render.com
2. Sign up with GitHub (same account)
3. Authorize Render to access GitHub
4. Dashboard → Click "New +"
5. Select "Web Service"
6. Connect repository: "chartlink-backend"
7. Fill settings:
   - Name: chartlink-api
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn app:app
   - Instance Type: Free
8. Environment Variables:
   - Key: DATABASE_URL
   - Value: [paste your Neon connection string]
9. Click "Create Web Service"
10. Wait for deployment (2-3 minutes)
    - You'll see: "Live"
```

### Step 2.4: Get API URL
```
1. Render dashboard → Your service shows
2. Copy URL: https://chartlink-api.onrender.com
3. Save this - you'll need it for frontend
4. Test: Open https://chartlink-api.onrender.com/health
   - Should show: {"status": "healthy"}
```

✅ **Backend deployed!**

---

## Phase 3: Deploy Frontend (5 minutes)

### Step 3.1: Update Environment
```
1. Open: frontend/.env.local
2. Replace NEXT_PUBLIC_API_URL=... with your Render URL
3. Example:
   NEXT_PUBLIC_API_URL=https://chartlink-api.onrender.com
4. Save file
```

### Step 3.2: Prepare GitHub
```
1. Go to https://github.com
2. Create new repository: "chartlink-frontend"
3. Description: "Stock screener dashboard"
4. Make it PUBLIC
5. Click "Create repository"
```

### Step 3.3: Push Frontend to GitHub
```bash
cd frontend

# Initialize git
git init
git add .
git commit -m "Initial frontend dashboard"

# Connect to GitHub
git remote add origin https://github.com/YOUR_USERNAME/chartlink-frontend.git
git branch -M main
git push -u origin main

# You should see: ✓ Done (all files pushed)
```

### Step 3.4: Deploy to Vercel
```
1. Go to https://vercel.com
2. Sign up with GitHub (same account)
3. Authorize Vercel to access GitHub
4. Import → Select "chartlink-frontend"
5. Settings auto-filled
6. Environment Variables:
   - Key: NEXT_PUBLIC_API_URL
   - Value: https://chartlink-api.onrender.com
7. Click "Deploy"
8. Wait for deployment (1-2 minutes)
   - You'll see: "Production"
```

### Step 3.5: Get Dashboard URL
```
1. Vercel dashboard → Your project shows
2. Copy URL: https://chartlink-frontend.vercel.app
3. (Note: Vercel generates the exact URL)
4. Test: Open the URL in browser
   - Should show: Dashboard with "🔴 LIVE" indicator
   - Loading message while fetching data
```

✅ **Frontend deployed!**

---

## Phase 4: Setup Local Selenium (5 minutes)

### Step 4.1: Download ChromeDriver
```
1. Go to https://chromedriver.chromium.org/
2. Find your Chrome version: Menu → About Google Chrome
3. Download matching ChromeDriver version
4. Extract to:
   - Windows: C:\chromedriver.exe
   - Mac: /usr/local/bin/chromedriver
   - Linux: /usr/local/bin/chromedriver
5. Verify: Open terminal/cmd
   - chromedriver --version
   - Should show version number
```

### Step 4.2: Update Selenium Configuration
```
1. Open: selenium/scraper.py
2. Find line: API_URL = "https://..."
3. Replace with your Render URL:
   API_URL = "https://chartlink-api.onrender.com"
4. Find line: download_path = r"..."
5. Update to your desired path:
   Windows: r"C:\Users\saikumar\Desktop\chartlink\15_minute"
   Mac/Linux: /Users/yourname/chartlink/15_minute
6. Save file
```

### Step 4.3: Install Dependencies
```bash
cd selenium

# Install packages
pip install -r requirements.txt

# Verify installation
pip list | grep -E "selenium|pandas|requests"
# Should show:
# pandas 2.0.3
# requests 2.31.0
# selenium 4.13.0
```

### Step 4.4: Test Selenium
```bash
# Run once to test
python scraper.py

# You should see:
# ✓ Browser loaded
# ✓ CSV clicked
# ✓ Read 50 rows from CSV
# ✓ API Response: {'status': 'success', 'rows': 50}
# ✓ Renamed to: 15_minutes_20260131_100012.csv
# ⏳ Waiting 60 seconds...

# Press Ctrl+C to stop (for first test)
```

✅ **Selenium ready!**

---

## Phase 5: Verify Everything Works (5 minutes)

### Step 5.1: Test API Endpoints
```bash
# In terminal/Postman, test each endpoint:

# Health check
curl https://chartlink-api.onrender.com/health
# Response: {"status": "healthy"}

# Get stats (will be empty first time)
curl https://chartlink-api.onrender.com/api/dashboard/stats
# Response: {...stats...}

# Get top gainers (will be empty first time)
curl https://chartlink-api.onrender.com/api/analytics/top-gainers
# Response: [...]
```

### Step 5.2: Test Dashboard
```
1. Open browser: https://chartlink-frontend.vercel.app
2. You should see:
   - Dashboard title
   - 🔴 LIVE indicator
   - Stats boxes (may show 0 data first time)
   - Multiple tables (empty initially)
3. If error: Check browser console (F12 → Console tab)
   - Look for API connection errors
```

### Step 5.3: Run Scraper (First Time)
```bash
cd selenium
python scraper.py

# Wait 3 minutes
# You should see:
# ✓ Browser loaded
# ✓ CSV clicked
# ✓ Read 50 rows
# ✓ API Response: success
```

### Step 5.4: Check Dashboard Updates
```
1. Refresh dashboard page
2. Should see data appearing:
   - Stats boxes now show numbers
   - Top gainers table populated
   - Momentum table populated
   - Breakout table populated
3. Data should update every 5 minutes automatically
```

✅ **Everything works!**

---

## Phase 6: Run Scraper 24/7 (Setup Once)

### Option A: Windows Task Scheduler (24/7)
```
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Chartlink Stock Scraper"
4. Trigger: At startup (or daily at 9:00 AM)
5. Action:
   - Program: python.exe
   - Arguments: C:\path\to\scraper.py
   - Start in: C:\path\to\selenium\
6. Click OK
7. Task will run automatically
```

### Option B: Windows Command (Manual)
```bash
cd selenium
python scraper.py
# Window will run until you close it or 3:30 PM
# Run this in the morning before market opens
```

### Option C: Mac/Linux Background
```bash
cd selenium
nohup python scraper.py > scraper.log 2>&1 &
# Runs in background, logs saved to scraper.log
```

---

## ✅ Final Verification Checklist

```
DATABASE
[ ] Neon account created
[ ] Database "chartlink" exists
[ ] Connection string tested
[ ] DATABASE_URL in backend/.env

BACKEND
[ ] Code pushed to GitHub
[ ] Render deployment successful
[ ] Health endpoint responds
[ ] API_URL working
[ ] Database populated with data

FRONTEND
[ ] Code pushed to GitHub
[ ] Vercel deployment successful
[ ] Dashboard loads
[ ] Auto-refresh works every 5 min
[ ] Shows live data

SELENIUM
[ ] ChromeDriver installed
[ ] Python packages installed
[ ] scraper.py configured with API_URL
[ ] Test run successful
[ ] Scheduled for 24/7 or running

INTEGRATION
[ ] Selenium pulls every 1 minute
[ ] Data appears in database
[ ] Dashboard refreshes every 5 min
[ ] All 4 analytics tables show data
[ ] Everything is LIVE and working
```

---

## 🎯 What Happens After Setup

```
Every 1 minute:
├─ Selenium pulls CSV
├─ Sends to API
└─ Data stored in database

Every 5 minutes:
├─ Dashboard auto-refreshes
├─ API calculates analytics
├─ Backend queries database
└─ Frontend displays live results

You get:
├─ Market overview stats
├─ Top gainers ranking
├─ Momentum detection
├─ Breakout identification
└─ All automatically!
```

---

## 🚨 Troubleshooting During Setup

| Problem | Solution |
|---------|----------|
| ChromeDriver not found | Add to PATH or specify full path in scraper.py |
| API returns 500 error | Check Render logs for DATABASE_URL error |
| Dashboard shows no data | Wait 5 minutes after scraper starts |
| "Connection refused" | Verify API_URL is correct in .env.local |
| Selenium won't download | Check download folder permissions |
| Frontend deploy fails | Check package.json for syntax errors |

---

## 📞 Support & Monitoring

### Check Logs
```
Render (Backend):  render.com → Your service → Logs
Vercel (Frontend): vercel.com → Your project → Analytics
Neon (Database):   console.neon.tech → Your project → Monitoring
```

### Monitor Health
```
API Status:  https://chartlink-api.onrender.com/health
Dashboard:   https://chartlink-frontend.vercel.app
```

---

## 🎉 You're Done!

All deployed and running automatically:

✅ Selenium pulling data every 1 minute  
✅ Backend processing with analytics  
✅ Database storing everything  
✅ Dashboard updating every 5 minutes  
✅ Users seeing live data automatically  

**Cost: $0/month**
**Maintenance: Minimal**
**Performance: Optimized for free tier**

---

**Deployment Complete! 🚀**
