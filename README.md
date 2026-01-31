# Chartlink Stock Screener

Complete implementation for 1-minute data pulling + 5-minute dashboard refresh.

## Project Structure

```
chartlink-app/
├── backend/          # Flask API (Render)
├── frontend/         # Next.js Dashboard (Vercel)
└── selenium/         # Data Scraper (Local)
```

## Prerequisites

- PostgreSQL Database (Neon.tech)
- GitHub Account (for deployments)
- Node.js 18+ (for frontend)
- Python 3.9+ (for backend & selenium)
- Chrome/Chromium browser (for selenium)
- ChromeDriver (for selenium)

## Setup Instructions

### 1. Database Setup (Neon)

1. Go to https://neon.tech
2. Sign up with GitHub
3. Create new project named "chartlink"
4. Copy connection string: `postgresql://user:password@ep-xyz.neon.tech/chartlink`
5. Save it in `backend/.env` as `DATABASE_URL`

### 2. Backend Setup (Render)

```bash
cd backend

# Update .env with your Neon connection string
# Add DATABASE_URL=your_neon_connection_string

# Initialize git
git init
git add .
git commit -m "Initial backend"
git branch -M main

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/chartlink-backend.git
git push -u origin main
```

Deploy on Render:
1. Go to https://render.com
2. Sign up with GitHub
3. Create new Web Service
4. Select `chartlink-backend` repository
5. Set runtime to Python 3.11
6. Add environment variable:
   - Key: `DATABASE_URL`
   - Value: Your Neon connection string
7. Deploy

Your API will be at: `https://chartlink-api.onrender.com`

### 3. Frontend Setup (Vercel)

```bash
cd frontend

# Install dependencies
npm install

# Update .env.local with your API URL
# NEXT_PUBLIC_API_URL=https://chartlink-api.onrender.com

# Test locally
npm run dev
# Visit http://localhost:3000

# Push to GitHub
git init
git add .
git commit -m "Initial frontend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/chartlink-frontend.git
git push -u origin main
```

Deploy on Vercel:
1. Go to https://vercel.com
2. Sign up with GitHub
3. Import `chartlink-frontend` repository
4. Add environment variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://chartlink-api.onrender.com`
5. Deploy

Your dashboard will be at: `https://chartlink-frontend.vercel.app`

### 4. Selenium Scraper (Local Machine)

```bash
cd selenium

# Install dependencies
pip install -r requirements.txt

# Download ChromeDriver from: https://chromedriver.chromium.org/
# Ensure it's in your PATH

# Update scraper.py
# Set API_URL = "https://chartlink-api.onrender.com"

# Run scraper
python scraper.py
```

The scraper will:
- Pull data every 1 minute
- Send to API
- Rename files with timestamp
- Stop at 3:30 PM

## API Endpoints

### Insert Data
**POST** `/api/data/insert`
- Bulk insert stock data from CSV
- Payload: Array of stock records

### Get Latest Data
**GET** `/api/dashboard/latest`
- Returns last 5 minutes of data
- Used by dashboard

### Get Stats
**GET** `/api/dashboard/stats`
- Returns market overview statistics
- Total symbols, market avg, gainers, losers

### Get Top Gainers
**GET** `/api/analytics/top-gainers`
- Top 20 gaining stocks (1-hour window)
- Used for dashboard table

### Health Check
**GET** `/health`
- Database connection status
- Used by monitoring

## Monitoring

### Uptime Monitoring (Optional)
1. Go to https://uptimerobot.com
2. Create new HTTP(S) monitor
3. URL: `https://chartlink-api.onrender.com/health`
4. Interval: 5 minutes
5. Alerts: Email

### Logs
- **Backend**: Render dashboard → Logs
- **Frontend**: Vercel dashboard → Analytics
- **Scraper**: Console output (local)

## Troubleshooting

### Backend won't connect to database
- Verify DATABASE_URL in Render env vars
- Check Neon database status
- Test connection locally

### Scraper not sending data
- Check API_URL in scraper.py
- Verify ChromeDriver path
- Check CSV file format
- Review console logs

### Dashboard shows no data
- Verify API_URL in frontend/.env.local
- Check API endpoints responding
- Review Render logs for errors
- Ensure scraper is running

### Data not persisting
- Check PostgreSQL table exists
- Verify connection string correct
- Check disk space on Neon
- Review error logs

## Data Retention

- Database auto-deletes data older than 90 days
- CSVs stored locally can be archived manually
- Backup important data periodically

## Cost Summary

- **Neon**: Free tier (3GB storage)
- **Render**: Free tier (750 hrs/month)
- **Vercel**: Free tier (unlimited)
- **Total**: $0/month ✓

## Next Steps

1. Deploy backend to Render
2. Deploy frontend to Vercel
3. Start selenium scraper on local machine
4. Monitor dashboard at frontend URL
5. Set up uptime monitoring
