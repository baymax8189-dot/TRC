# Selenium Scraper

Automated data scraper that pulls stock data every 1 minute.

## Setup

```bash
pip install -r requirements.txt
```

## Prerequisites

1. Download ChromeDriver: https://chromedriver.chromium.org/
2. Add to PATH or specify in code
3. Update API_URL in scraper.py

## Configuration

Edit `scraper.py`:
- `download_path`: Where to save CSV files
- `API_URL`: Backend API URL
- `url`: Target screener URL
- `stop_time`: When to stop scraping (default: 3:30 PM)

## Run

```bash
python scraper.py
```

Scraper will:
- ✓ Load webpage
- ✓ Click CSV button every 1 minute
- ✓ Download CSV file
- ✓ Send to API
- ✓ Rename with timestamp
- ✓ Repeat until 3:30 PM

## Logs

Console shows:
- Download timestamps
- Records sent
- API responses
- Errors

## Tips

- Run on dedicated machine for 24/7 operation
- Use Windows Task Scheduler for auto-start
- Keep browser/chromedriver updated
- Monitor disk space for CSV files
