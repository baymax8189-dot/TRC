import asyncio
from playwright.async_api import async_playwright
import requests
import os
import pandas as pd
from datetime import datetime

# CONFIG
API_URL = os.environ.get('API_URL', 'https://your-backend.onrender.com/api/data/insert')
SCRAPE_URL = os.environ.get('SCRAPE_URL', 'https://example.com/your-stock-page')

async def scrape_and_send():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(SCRAPE_URL)
        # TODO: Replace below with your actual scraping logic
        # Example: Scrape a table into a DataFrame
        table_html = await page.inner_html('table#your-table-id')
        df = pd.read_html(table_html)[0]
        # Data cleaning/renaming as per your schema
        # df = ...
        # Convert to list of dicts
        data = df.to_dict('records')
        # Send to backend
        resp = requests.post(API_URL, json=data)
        print(f"POST {API_URL} status: {resp.status_code}")
        print(resp.text)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_and_send())
