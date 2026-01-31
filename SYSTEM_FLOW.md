# Complete System Flow

## Live Data Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SELENIUM SCRAPER (Local)                        │
│                                                                         │
│  Every 1 minute:                                                        │
│  1. Open Chartink screener page                                         │
│  2. Click CSV download                                                  │
│  3. Parse CSV file                                                      │
│  4. Send data to API                                                    │
│  5. Rename CSV with timestamp                                           │
│                                                                         │
│  API Call:                                                              │
│  POST https://chartlink-api.onrender.com/api/data/insert                │
│  Payload: [                                                             │
│    {symbol: "TTML", price: 49.21, pct_chg: 7.8, volume: 13089040}     │
│    {symbol: "L&T", price: 307.7, pct_chg: 2.81, volume: 3076003}      │
│    ...                                                                  │
│  ]                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        BACKEND API (Render)                             │
│                                                                         │
│  Receives raw data:                                                     │
│  POST /api/data/insert                                                  │
│  → Stores in PostgreSQL                                                 │
│  → Creates records with timestamps                                      │
│  → Response: {"status": "success", "rows": 50}                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE (Neon)                           │
│                                                                         │
│  Table: stocks                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ id │ symbol │ price │ pct_chg │ volume │ created_at │ ...       │  │
│  ├───────────────────────────────────────────────────────────────────┤  │
│  │ 1  │ TTML   │ 49.21 │  7.8    │ 13M    │ 10:01:05   │           │  │
│  │ 2  │ L&T    │ 307.7 │  2.81   │ 3M     │ 10:01:05   │           │  │
│  │ 3  │ GODRY  │ 2711.8│  2.49   │ 172k   │ 10:01:05   │           │  │
│  │... │ ...    │ ...   │ ...     │ ...    │ ...        │           │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Every 1 minute: 50+ rows added to database                             │
│  Total data: 90 days retention                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                       EVERY 5 MINUTES DASHBOARD REFRESH
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    ANALYTICS LAYER (Backend)                            │
│                                                                         │
│  Dashboard calls: /api/dashboard/stats                                  │
│  ↓ Query database for last 1 hour data                                  │
│  ↓ Calculate metrics                                                    │
│  ↓ Return:                                                              │
│  {                                                                      │
│    "total_symbols": 50,                                                 │
│    "market_avg": 2.15,                                                  │
│    "gainers_5pct": 12,                                                  │
│    "losers_5pct": 5,                                                    │
│    "total_volume": 450000000                                            │
│  }                                                                      │
│                                                                         │
│  Dashboard calls: /api/analytics/top-gainers                            │
│  ↓ Query database for best performers                                   │
│  ↓ Group by symbol & calculate averages                                 │
│  ↓ Return top 20 ranked by gain                                         │
│  [                                                                      │
│    {symbol: "TTML", avg_gain: 7.8, max_price: 49.21, ...}             │
│    {symbol: "L&T", avg_gain: 2.81, max_price: 308, ...}               │
│    ...                                                                  │
│  ]                                                                      │
│                                                                         │
│  Dashboard calls: /api/analytics/momentum                               │
│  ↓ Find stocks with consistent upward trend (30 min)                    │
│  ↓ Require minimum occurrences for confirmation                         │
│  ↓ Return momentum leaders                                              │
│                                                                         │
│  Dashboard calls: /api/analytics/breakouts                              │
│  ↓ Detect high volatility & price movement                              │
│  ↓ Calculate breakout probability                                       │
│  ↓ Return breakout candidates                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND DASHBOARD (Vercel)                          │
│                                                                         │
│  📊 STOCK SCREENER DASHBOARD                                            │
│  🔴 LIVE | Last loaded: 10:05:15 | Auto-refreshes every 5 min          │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Total Symbols: 50  │ Market Avg: +2.15%                        │   │
│  │ Gainers >5%: 12    │ Losers <-5%: 5                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  🚀 TOP GAINERS (Last Hour)                                             │
│  ┌──────────┬──────────┬─────────┬──────────┐                          │
│  │ Symbol   │ Avg Gain │ Price   │ Volume   │                          │
│  ├──────────┼──────────┼─────────┼──────────┤                          │
│  │ TTML     │ +7.8%    │ ₹49.21  │ 13.1M    │                          │
│  │ L&T      │ +2.81%   │ ₹307.7  │ 3.1M     │                          │
│  │ GODRY    │ +2.49%   │ ₹2711.8 │ 172k     │                          │
│  └──────────┴──────────┴─────────┴──────────┘                          │
│                                                                         │
│  ⚡ MOMENTUM STOCKS (Strong Upward Trend)                               │
│  [Similar table with momentum data]                                     │
│                                                                         │
│  🚀 BREAKOUT STOCKS (High Volatility)                                   │
│  [Similar table with breakout data]                                     │
│                                                                         │
│  📈 LATEST DATA (Last 5 min)                                            │
│  [Raw data table]                                                       │
│                                                                         │
│  ✓ User sees LIVE data                                                  │
│  ✓ No refresh button clicks needed                                      │
│  ✓ Auto-updates every 5 minutes                                         │
│  ✓ Based on 1-minute data pulls from backend                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                            USERS VIEWING
                        (0 API calls from them)
                        (Backend does all work)
```

## Timing Diagram

```
TIME        SELENIUM    DATABASE    ANALYTICS      DASHBOARD
────────────────────────────────────────────────────────────────
10:00:00    PULL ✓      INSERT ✓    
10:00:01    
10:00:02    
10:01:00    PULL ✓      INSERT ✓    
10:02:00    PULL ✓      INSERT ✓    
10:03:00    PULL ✓      INSERT ✓    
10:04:00    PULL ✓      INSERT ✓    
10:05:00    PULL ✓      INSERT ✓    CALCULATE    FETCH ✓
10:05:01                             └─ Market    └─ Display
10:05:02                             └─ Gainers   └─ Update
10:05:03                             └─ Momentum  └─ Show LIVE
10:05:04                             └─ Breakouts └─ Users see
10:06:00    PULL ✓      INSERT ✓    
10:07:00    PULL ✓      INSERT ✓    
10:08:00    PULL ✓      INSERT ✓    
10:09:00    PULL ✓      INSERT ✓    
10:10:00    PULL ✓      INSERT ✓    CALCULATE    FETCH ✓
             ...         ...        └─ Updates   └─ Display
```

## Resource Usage

```
Per Hour:
├─ Selenium: 60 API calls (1 per minute)
│  └─ Each: 50 records × 200 bytes = 10KB
│  └─ Total: 600KB per hour
│
├─ Dashboard: 12 API calls (1 per 5 minutes)
│  └─ Each: ~5KB (processed data)
│  └─ Total: 60KB per hour
│
├─ Database: ~1GB per day (50 symbols × 1440 min × 500B)
│  └─ Auto-cleanup after 90 days
│
└─ Backend Processing: Minimal
   └─ Database queries: ~100ms each
   └─ CPU: <5% idle server
   └─ Memory: <50MB

Free Tier Capacity:
├─ Render: 750 hours/month ← Uses <1% ✓
├─ Neon: 3GB storage ← Uses ~90GB/month (auto-deleted) ✓
└─ Vercel: Unlimited bandwidth ← Uses minimal ✓

Cost: $0/month ✓
```

## What Users See (Without Doing Anything)

1. **Open Dashboard**
   - Loads latest data from database
   - Shows live stats and rankings
   - No loading spinner needed

2. **Leave Dashboard Open**
   - Auto-refreshes every 5 minutes
   - Fetches fresh analytics
   - Updates all tables
   - Shows "Last loaded: XX:XX:XX"

3. **Backend Works Automatically**
   - Selenium pulls every minute
   - Analytics processes every 5 minutes
   - Database stays updated
   - No maintenance needed

4. **Users Get Live Data**
   - Market trends in real-time
   - Top performers identified automatically
   - Momentum stocks highlighted
   - Breakout candidates detected
   - All without clicking anything

## Why This Is Better Than Auto-Refresh Every Minute

❌ **Every 1 minute refresh:**
- 60 dashboard requests/hour
- Strains API server
- Uses more Render hours
- Network overhead
- Battery drain on client

✅ **Every 5 minute refresh (smart analytics):**
- 12 dashboard requests/hour
- Light API load
- Stays on free tier easily
- Processed data only (no raw calculation)
- Client-side minimal

✅ **Plus 1-minute backend updates:**
- Data always fresh in database
- Analytics always up-to-date
- Users see latest info on each refresh
- Best of both worlds
