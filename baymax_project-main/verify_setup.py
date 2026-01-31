#!/usr/bin/env python3
"""
Setup verification script
Run this to check if everything is configured correctly
"""

import os
import sys

def check_backend():
    print("\n📦 Backend Files:")
    backend_files = [
        'backend/app.py',
        'backend/requirements.txt',
        'backend/.env',
        'backend/Procfile',
        'backend/render.yaml'
    ]
    for f in backend_files:
        status = "✓" if os.path.exists(f) else "✗"
        print(f"  {status} {f}")

def check_frontend():
    print("\n🎨 Frontend Files:")
    frontend_files = [
        'frontend/package.json',
        'frontend/.env.local',
        'frontend/pages/dashboard.jsx',
        'frontend/pages/index.jsx',
        'frontend/next.config.js'
    ]
    for f in frontend_files:
        status = "✓" if os.path.exists(f) else "✗"
        print(f"  {status} {f}")

def check_selenium():
    print("\n🤖 Selenium Files:")
    selenium_files = [
        'selenium/scraper.py',
        'selenium/requirements.txt'
    ]
    for f in selenium_files:
        status = "✓" if os.path.exists(f) else "✗"
        print(f"  {status} {f}")

def check_docs():
    print("\n📚 Documentation Files:")
    doc_files = [
        'README.md',
        'CHECKLIST.md',
        'QUICKSTART.sh',
        '.gitignore'
    ]
    for f in doc_files:
        status = "✓" if os.path.exists(f) else "✗"
        print(f"  {status} {f}")

if __name__ == '__main__':
    print("=" * 50)
    print("Chartlink - Setup Verification")
    print("=" * 50)
    
    check_backend()
    check_frontend()
    check_selenium()
    check_docs()
    
    print("\n" + "=" * 50)
    print("Next Steps:")
    print("=" * 50)
    print("""
1. Read README.md for detailed setup instructions

2. Setup Database:
   - Create Neon account at https://neon.tech
   - Create database and copy connection string
   - Update backend/.env with DATABASE_URL

3. Deploy Backend:
   - cd backend
   - Push to GitHub
   - Deploy to Render.com
   - Copy API URL

4. Deploy Frontend:
   - cd frontend
   - Update .env.local with API URL
   - Push to GitHub
   - Deploy to Vercel
   - Copy Dashboard URL

5. Run Scraper:
   - cd selenium
   - pip install -r requirements.txt
   - Download ChromeDriver
   - Update API_URL in scraper.py
   - python scraper.py

6. Monitor:
   - Open Dashboard URL
   - Verify data loading
   - Check logs
    """)
