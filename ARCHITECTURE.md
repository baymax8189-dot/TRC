# Complete Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                    CHARTLINK STOCK SCREENER SYSTEM                      │
│                                                                         │
│  Three Core Components:                                                 │
│  1. Data Collection (Selenium) - Local                                  │
│  2. Backend & Database (Render + Neon) - Cloud                          │
│  3. Frontend Dashboard (Vercel) - Cloud                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

                              COMPONENT 1: SELENIUM
┌─────────────────────────────────────────────────────────────────────────┐
│  Your Local Machine (Windows/Mac/Linux)                                 │
│                                                                         │
│  scraper.py (Python)                                                    │
│  ├─ 10:00:00 → Open Chrome → Chartink screener                         │
│  ├─ 10:00:05 → Click CSV button                                        │
│  ├─ 10:00:08 → Wait for download (downloaded_file.csv)                 │
│  ├─ 10:00:10 → Read CSV (50 stock rows)                                │
│  ├─ 10:00:11 → Send HTTP POST to API                                   │
│  │              URL: https://api.onrender.com/api/data/insert          │
│  │              Body: [                                                │
│  │                {Symbol: "TTML", Price: 49.21, %Chg: 7.8, ...}     │
│  │                {Symbol: "L&T", Price: 307.7, %Chg: 2.81, ...}     │
│  │                ...                                                  │
│  │              ]                                                      │
│  ├─ 10:00:12 → API responds: {"status": "success", "rows": 50}         │
│  ├─ 10:00:13 → Rename CSV: 15_minutes_20260131_100012.csv             │
│  ├─ 10:00:14 → Done for this minute                                    │
│  └─ 10:01:00 → Repeat (every 1 minute)                                 │
│                                                                         │
│  Logs:                                                                  │
│  ✓ Browser loaded                                                       │
│  ✓ CSV clicked                                                          │
│  ✓ Read 50 rows                                                         │
│  ✓ API Response: success                                                │
│  ✓ Renamed file                                                         │
│  ⏳ Waiting 60 seconds...                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                          HTTPS POST Request
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│              COMPONENT 2: BACKEND API (Render.com)                      │
│                                                                         │
│  Flask Application (Python)                                             │
│  URL: https://chartlink-api.onrender.com                                │
│                                                                         │
│  Endpoint: POST /api/data/insert                                        │
│  ├─ Receives: Array of stock objects                                    │
│  ├─ Validates: Check data format                                        │
│  ├─ Prepares: Create bulk insert statement                              │
│  └─ Executes: INSERT 50 rows into database                              │
│                                                                         │
│  Logs:                                                                  │
│  ✓ Inserted 50 records at 10:00:12                                      │
│                                                                         │
│  Endpoint: GET /api/dashboard/stats                                     │
│  ├─ Called by: Dashboard every 5 minutes                                │
│  ├─ Logic: get_market_overview()                                        │
│  │   └─ Query database for latest data                                  │
│  │   └─ Calculate: Count, average, gainers, losers, volume             │
│  └─ Returns: {                                                          │
│              "total_symbols": 50,                                       │
│              "market_avg": 2.15,                                        │
│              "gainers_5pct": 12,                                        │
│              "losers_5pct": 5,                                          │
│              "total_volume": 450000000,                                 │
│              "timestamp": "2026-01-31T10:05:00Z"                        │
│            }                                                            │
│                                                                         │
│  Endpoint: GET /api/analytics/top-gainers                               │
│  ├─ Called by: Dashboard every 5 minutes                                │
│  ├─ Logic: get_top_performers()                                         │
│  │   └─ Query: Last 1 hour of data                                      │
│  │   └─ Group by: Symbol                                                │
│  │   └─ Calculate: Avg gain, max price, volume, count                   │
│  │   └─ Sort: By avg gain DESC                                          │
│  │   └─ Limit: Top 25                                                   │
│  └─ Returns: [                                                          │
│              {symbol: "TTML", avg_gain: 7.8, max_price: 49.21, ...},  │
│              {symbol: "L&T", avg_gain: 2.81, max_price: 308, ...},    │
│              ...                                                        │
│            ]                                                            │
│                                                                         │
│  Endpoint: GET /api/analytics/momentum                                  │
│  ├─ Called by: Dashboard every 5 minutes                                │
│  ├─ Logic: get_momentum_stocks()                                        │
│  │   └─ Time window: 30 minutes                                         │
│  │   └─ Filter: Avg gain > 0, Count ≥ 25                                │
│  │   └─ Calculate: Volatility                                           │
│  │   └─ Sort: By gain DESC, appearances DESC                            │
│  └─ Returns: Top momentum stocks                                        │
│                                                                         │
│  Endpoint: GET /api/analytics/breakouts                                 │
│  ├─ Called by: Dashboard every 5 minutes                                │
│  ├─ Logic: get_breakout_analysis()                                      │
│  │   └─ Time window: 15 minutes                                         │
│  │   └─ Calculate: Price high/low, range, volatility                    │
│  │   └─ Filter: Range > 2% of average price                             │
│  │   └─ Sort: By max gain DESC                                          │
│  └─ Returns: Breakout candidates                                        │
│                                                                         │
│  Database Connection:                                                   │
│  ├─ psycopg2 connects to PostgreSQL (Neon)                              │
│  ├─ Uses connection pooling                                             │
│  ├─ Queries use indexed columns (symbol, created_at)                    │
│  └─ Keeps 90 days of data (auto-cleanup)                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                          HTTPS GET/POST Requests
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│         COMPONENT 2B: DATABASE (Neon - PostgreSQL)                      │
│                                                                         │
│  Server: ep-xyz.neon.tech                                               │
│  Database: chartlink                                                    │
│                                                                         │
│  Table: stocks (50+ records per minute)                                 │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ id  │ symbol │ price  │ pct_chg │ volume      │ created_at        │ │
│  ├────────────────────────────────────────────────────────────────────┤ │
│  │ 1   │ TTML   │ 49.21  │  7.8    │ 13089040    │ 2026-01-31 10:00  │ │
│  │ 2   │ L&T    │ 307.7  │  2.81   │ 3076003     │ 2026-01-31 10:00  │ │
│  │ 3   │ GODRY  │ 2711.8 │  2.49   │ 172649      │ 2026-01-31 10:00  │ │
│  │ 4   │ TTML   │ 49.25  │  7.85   │ 13100000    │ 2026-01-31 10:01  │ │
│  │ ... │ ...    │ ...    │ ...     │ ...         │ ...               │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  Indexes:                                                               │
│  ├─ idx_symbol → Fast lookup by stock symbol                            │
│  ├─ idx_timestamp → Fast queries by time range                          │
│  └─ idx_created → Fast sorting by creation time                         │
│                                                                         │
│  Storage:                                                               │
│  ├─ ~500 bytes per row                                                  │
│  ├─ 50 rows per minute × 1440 min = 72,000 rows/day                     │
│  ├─ ~36MB per day                                                       │
│  ├─ ~1GB per month                                                      │
│  ├─ Auto-delete older than 90 days                                      │
│  └─ Free tier: 3GB limit (plenty!)                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                          HTTPS GET Requests (5 min)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│          COMPONENT 3: FRONTEND DASHBOARD (Vercel)                       │
│                                                                         │
│  URL: https://chartlink-frontend.vercel.app                             │
│  Framework: Next.js + React (JavaScript)                                │
│                                                                         │
│  On Page Load (First Visit):                                            │
│  ├─ Fetch 5 endpoints from API                                          │
│  ├─ Render stats box                                                    │
│  ├─ Render 4 data tables                                                │
│  └─ Display to user                                                     │
│                                                                         │
│  Every 5 Minutes (Auto-Refresh):                                        │
│  ├─ useEffect hook triggers                                             │
│  ├─ Fetch stats: GET /api/dashboard/stats                               │
│  ├─ Fetch top gainers: GET /api/analytics/top-gainers                   │
│  ├─ Fetch momentum: GET /api/analytics/momentum                         │
│  ├─ Fetch breakouts: GET /api/analytics/breakouts                       │
│  ├─ Fetch latest: GET /api/dashboard/latest                             │
│  ├─ Update all tables                                                   │
│  ├─ Update "Last loaded" timestamp                                      │
│  └─ Users see fresh LIVE data                                           │
│                                                                         │
│  UI Layout:                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ 📊 STOCK SCREENER DASHBOARD        🔴 LIVE  [🔄 Refresh]       │   │
│  │ Last loaded: 10:05:15 | Auto-refreshes every 5 min              │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ [Total Symbols: 50] [Market Avg: +2.15%]                        │   │
│  │ [Gainers >5%: 12]   [Losers <-5%: 5]                            │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ 🚀 TOP GAINERS (Last Hour)                                       │   │
│  │ │ Symbol  │ Avg Gain │ Max Price │ Volume      │ Count │        │   │
│  │ ├─────────┼──────────┼───────────┼─────────────┼───────┤        │   │
│  │ │ TTML    │ +7.8%    │ ₹49.21    │ 13,089,040  │ 50    │        │   │
│  │ │ L&T     │ +2.81%   │ ₹307.7    │ 3,076,003   │ 48    │        │   │
│  │ │ GODRY   │ +2.49%   │ ₹2711.8   │ 172,649     │ 47    │        │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ ⚡ MOMENTUM STOCKS (Strong Upward Trend - 30 min)                │   │
│  │ │ Symbol  │ Avg Gain │ Appearances │ Volatility │ Updated │     │   │
│  │ ├─────────┼──────────┼─────────────┼────────────┼─────────┤     │   │
│  │ │ TTML    │ +7.8%    │ 50          │ 0.45%      │ 10:05   │     │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ 🚀 BREAKOUT STOCKS (High Volatility - 15 min)                    │   │
│  │ │ Symbol  │ Max Gain │ Price Range │ Avg Volume  │ Updated │    │   │
│  │ ├─────────┼──────────┼─────────────┼─────────────┼─────────┤    │   │
│  │ │ TTML    │ +7.8%    │ ₹0.50       │ 13,000,000  │ 10:05   │    │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ 📈 LATEST DATA (Last 5 minutes - Raw data)                       │   │
│  │ [Table with 50+ latest stock records]                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  User Experience:                                                       │
│  ├─ Opens dashboard URL                                                │
│  ├─ Sees LIVE data immediately                                         │
│  ├─ Page auto-updates every 5 minutes                                   │
│  ├─ Can click "Refresh" button for instant update                       │
│  ├─ No configuration needed                                             │
│  ├─ Works on desktop & mobile                                           │
│  └─ See real-time market data automatically                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                        USER VIEWS LIVE DATA
```

## Communication Flow Detailed

```
╔═══════════════════════════════════════════════════════════════════════╗
║                         TIME: 10:05:00 AM                             ║
╚═══════════════════════════════════════════════════════════════════════╝

STEP 1: Selenium Pulls (Every 1 minute)
─────────────────────────────────────────
User's Computer          Chartink                    API (Render)
       │                    │                             │
       └──── Browse ────────→ Chartink Screener          │
       │                    │                             │
       └──── Click CSV ─────→ Download starts            │
       │                    │                             │
       └──── Parse CSV ─────→ 50 stock records           │
       │                    │                             │
       └──── POST /api/data/insert ───────────────────────→
              (50 records)                                │
                                                         ├─ Validate
                                                         ├─ Insert DB
                                                         └─ Return 200
                                                         │
       ←────────────────── {"status": "success"} ────────┘

DATABASE (Neon)
       ↓
   UPDATED: 50 new rows

STEP 2: User Opens Dashboard
──────────────────────────────
Browser (Vercel)                       API (Render)         Database (Neon)
       │                                  │                      │
       └─ GET /api/dashboard/stats ──────→ Query database       │
       │                                  └─ SELECT stats ─────→│
       │                                  ← Return data ←────────┘
       │ ←───────────────────────────────┘
       │
       └─ GET /api/analytics/top-gainers ─→ Query database
       │                                  └─ SELECT gainers ───→
       │                                  ← Return data ←────────
       │ ←───────────────────────────────┘
       │
       └─ GET /api/analytics/momentum ────→ Query database
       │                                  └─ SELECT momentum ───→
       │                                  ← Return data ←────────
       │ ←───────────────────────────────┘
       │
       └─ GET /api/analytics/breakouts ───→ Query database
       │                                  └─ SELECT breakouts ──→
       │                                  ← Return data ←────────
       │ ←───────────────────────────────┘
       │
       └─ GET /api/dashboard/latest ──────→ Query database
                                          └─ SELECT latest ────→
                                          ← Return data ←────────
       ←───────────────────────────────┘

BROWSER
       ↓
   RENDER: Dashboard with all 4 tables populated with LIVE data
   DISPLAY: Latest market stats, top gainers, momentum, breakouts

STEP 3: Wait 5 Minutes
───────────────────────
       (Repeat Step 2 automatically via setInterval)

RESULT: Users see constantly updated LIVE data without clicking anything
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TECHNOLOGY STACK                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DATA COLLECTION                                                        │
│  ├─ Language: Python 3.9+                                               │
│  ├─ Framework: Selenium 4.13                                            │
│  ├─ Browser: Chrome/Chromium                                            │
│  ├─ Libraries: Pandas, Requests                                         │
│  └─ Deployment: Your Local Machine (24/7)                               │
│                                                                         │
│  BACKEND API                                                            │
│  ├─ Language: Python 3.11                                               │
│  ├─ Framework: Flask 2.3                                                │
│  ├─ CORS: Flask-CORS                                                    │
│  ├─ Database Driver: psycopg2                                           │
│  ├─ WSGI Server: Gunicorn                                               │
│  ├─ Deployment: Render.com (Free)                                       │
│  └─ Port: 5000 (internal), 443 (HTTPS external)                         │
│                                                                         │
│  DATABASE                                                               │
│  ├─ System: PostgreSQL                                                  │
│  ├─ Provider: Neon (Free tier)                                          │
│  ├─ Storage: 3GB free (auto-cleanup 90 days)                            │
│  ├─ Backup: Automatic                                                   │
│  ├─ Tables: stocks (main data table)                                    │
│  └─ Indexes: symbol, timestamp, created_at                              │
│                                                                         │
│  FRONTEND                                                               │
│  ├─ Language: JavaScript (JSX)                                          │
│  ├─ Framework: Next.js 14                                               │
│  ├─ UI: React 18                                                        │
│  ├─ Styling: Inline CSS                                                 │
│  ├─ Deployment: Vercel (Free)                                           │
│  ├─ CDN: Global edge network                                            │
│  └─ Domain: chartlink-frontend.vercel.app                               │
│                                                                         │
│  MONITORING & LOGGING                                                   │
│  ├─ Backend Logs: Render console                                        │
│  ├─ Frontend Analytics: Vercel dashboard                                │
│  ├─ Database Logs: Neon dashboard                                       │
│  ├─ Local Logs: Console output (scraper)                                │
│  └─ Health Check: /health endpoint                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
                          INTERNET
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ↓                    ↓                    ↓
    VERCEL              RENDER                 NEON
   (Frontend)          (Backend API)        (Database)
        │                    │                    │
   Dashboard            Flask App            PostgreSQL
   Next.js              Python                Database
   React                API Endpoints         Data Storage
   UI                   Analytics Logic       Indexes
   80ms response        100ms response        Response time
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                  ← HTTPS ────┤──── HTTPS →
                             │
                        Your Browser
                             │
                      View Dashboard
                      See Live Data
                      Auto-refresh
                             │
                        ← HTTP Request ←
                             │
                      Every 5 Minutes
```

---

**Ready to see it in action? Follow the README.md setup guide!**
