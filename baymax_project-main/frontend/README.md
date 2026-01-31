# Frontend - Next.js Dashboard

Real-time stock screener dashboard with 5-minute auto-refresh.

## Setup

```bash
npm install
```

## Configuration

Create `.env.local`:
```
NEXT_PUBLIC_API_URL=https://chartlink-api.onrender.com
```

## Run Locally

```bash
npm run dev
```

Dashboard will be at: http://localhost:3000

## Build for Production

```bash
npm run build
npm start
```

## Features

- 📊 Dashboard overview stats
- 🚀 Top gainers table (1-hour)
- 📈 Latest data (5-minute)
- 🔄 Auto-refresh every 5 minutes
- 📱 Responsive design
- ⚡ Fast performance

## Deployment

Deploy to Vercel:
1. Push code to GitHub
2. Import in Vercel dashboard
3. Set NEXT_PUBLIC_API_URL env var
4. Deploy

## Customization

Edit `pages/dashboard.jsx` to customize:
- Refresh interval
- Data limits
- Styling
- Table columns
