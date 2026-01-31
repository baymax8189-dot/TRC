# Analytics Layer Architecture

## Overview

The system now has a **3-tier architecture** that separates data collection, processing, and presentation:

```
┌──────────────────────────────────────────────────────────────┐
│ TIER 1: DATA COLLECTION (Every 1 minute)                     │
├──────────────────────────────────────────────────────────────┤
│ Selenium Scraper                                              │
│ └─ Pulls CSV from Chartink                                    │
│ └─ Sends raw data to API                                      │
│ └─ Runs continuously throughout the day                       │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ TIER 2: DATABASE (Stores all data)                           │
├──────────────────────────────────────────────────────────────┤
│ PostgreSQL (Neon)                                             │
│ └─ stocks table with symbol, price, volume, % change         │
│ └─ Indexed for fast queries                                   │
│ └─ Retains 90 days of data                                    │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ TIER 3: ANALYTICS LAYER (Backend Logic - Every 5 minutes)    │
├──────────────────────────────────────────────────────────────┤
│ API Endpoints with Smart Logic                               │
│                                                               │
│ 1. get_market_overview()                                      │
│    └─ Calculates: Total symbols, market avg, gainers/losers  │
│                                                               │
│ 2. get_top_performers()                                       │
│    └─ Identifies: Best gainers, avg gains, volatility        │
│                                                               │
│ 3. get_momentum_stocks()                                      │
│    └─ Finds: Strong upward trend (last 30 min)              │
│                                                               │
│ 4. get_breakout_analysis()                                    │
│    └─ Detects: High volatility stocks (price movement)      │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ TIER 4: FRONTEND (Dashboard - Every 5 minutes)               │
├──────────────────────────────────────────────────────────────┤
│ React/Next.js Dashboard                                       │
│                                                               │
│ Auto-refreshes every 5 minutes                                │
│ Displays:                                                     │
│ ├─ Market overview stats                                      │
│ ├─ Top gainers table                                          │
│ ├─ Momentum stocks                                            │
│ ├─ Breakout stocks                                            │
│ └─ Latest raw data                                            │
│                                                               │
│ Users see LIVE data with NO manual refreshes needed           │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

```
10:00 AM
├─ 10:00:00 → Selenium pulls data
├─ 10:00:05 → Data stored in database
├─ 10:00:10 → Analytics calculated (if requested)
└─ 10:00:15 → Dashboard shows results

10:01 AM
├─ 10:01:00 → Selenium pulls data (update)
├─ 10:01:05 → Data stored in database
├─ 10:05:00 → Dashboard auto-refreshes (5 min interval)
│              └─ API runs analytics on new data
│              └─ Returns fresh results to dashboard
└─ Users see updated live data
```

## Analytics Functions

### 1. Market Overview
**Endpoint:** `/api/dashboard/stats`

Calculates in real-time:
- Total unique symbols
- Market average (weighted)
- Gainers > 5%
- Losers < -5%
- Total trading volume

### 2. Top Performers
**Endpoint:** `/api/analytics/top-gainers`

Uses database to find:
- Average gain per symbol (last hour)
- Maximum gain achieved
- Minimum gain in period
- Trading volume
- Occurrences in dataset

### 3. Momentum Stocks
**Endpoint:** `/api/analytics/momentum`

Identifies stocks with:
- Positive average gain (last 30 min)
- Minimum 25 occurrences (persistent trend)
- High price volatility
- Strong upward momentum

### 4. Breakout Analysis
**Endpoint:** `/api/analytics/breakouts`

Detects:
- Price high/low (15 min window)
- Price range volatility
- High trading volume
- Stocks moving >2% from average price

## Why This Architecture?

✅ **Separation of Concerns**
- Scraper only pulls data (doesn't analyze)
- Analytics layer only processes (doesn't scrape)
- Dashboard only displays (doesn't calculate)

✅ **Performance Optimized**
- Queries run on indexed database (fast)
- Analytics cached at API level
- Dashboard makes single call every 5 min (minimal load)

✅ **Scalability**
- Can add more analytics functions without changing UI
- Database can grow without affecting performance
- Analytics logic can be upgraded independently

✅ **Resource Efficient**
- Selenium runs lightweight
- Database stores compressed data
- API calculations only when dashboard requests
- Frontend receives processed data (no client-side calc)

✅ **Free Tier Friendly**
- Minimal API calls (12-15 per hour from dashboard)
- Queries optimized with indexes
- No real-time WebSockets needed

## Database Queries Used

### Top Gainers Query
```sql
SELECT 
    symbol, stock_name,
    ROUND(AVG(pct_chg), 2) as avg_gain,
    COUNT(*) as occurrences
FROM stocks
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY symbol, stock_name
HAVING COUNT(*) >= 3
ORDER BY avg_gain DESC
LIMIT 25
```

### Momentum Query
```sql
SELECT 
    symbol, stock_name,
    AVG(pct_chg) as avg_gain,
    COUNT(*) as appearances
FROM stocks
WHERE created_at > NOW() - INTERVAL '30 minutes'
GROUP BY symbol, stock_name
HAVING COUNT(*) >= 25 AND AVG(pct_chg) > 0
ORDER BY avg_gain DESC
LIMIT 20
```

## Real-Time Processing

When dashboard refreshes (every 5 min):

1. **Dashboard makes API call**
   ```
   GET /api/dashboard/stats
   GET /api/analytics/top-gainers
   GET /api/analytics/momentum
   GET /api/analytics/breakouts
   ```

2. **Backend queries database** (data already there from Selenium)
   ```
   SELECT ... WHERE created_at > NOW() - INTERVAL '30 minutes'
   ```

3. **Analytics logic processes data**
   - Calculates averages
   - Identifies patterns
   - Ranks by performance

4. **Returns processed data to frontend**
   ```json
   {
     "symbol": "TTML",
     "avg_gain": 7.8,
     "max_price": 49.21
   }
   ```

5. **Dashboard displays live results**

## System Benefits

| Aspect | Benefit |
|--------|---------|
| **Data Freshness** | Every 1 min (Selenium) |
| **Display Refresh** | Every 5 min (Dashboard) |
| **User Experience** | Live data, no clicks needed |
| **Performance** | Fast queries on indexed DB |
| **Scalability** | Can add 1000s of concurrent users |
| **Cost** | Stays on free tier |
| **Maintainability** | Clean separation of concerns |

## Future Enhancements

✅ Add more analytics:
- Volume surge detection
- Technical indicators (RSI, MACD)
- Price pattern recognition
- Sector-wise analysis

✅ Add alerts:
- Email when stock hits threshold
- SMS notifications
- Webhook integration

✅ Add history:
- Charts and graphs
- Historical comparisons
- Trend analysis

✅ Add ML:
- Predictive models
- Anomaly detection
- Clustering stocks by behavior
