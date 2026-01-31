# Backend - Flask API

API server for receiving stock data and serving dashboard queries.

## Setup

```bash
pip install -r requirements.txt
```

## Configuration

Create `.env` file:
```
DATABASE_URL=postgresql://user:password@ep-xyz.neon.tech/chartlink
PORT=5000
```

## Run Locally

```bash
python app.py
```

API will be at: http://localhost:5000

## Deployment

Deploy to Render using `render.yaml` configuration.
