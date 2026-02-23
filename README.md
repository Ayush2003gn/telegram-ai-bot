# Telegram AI Bot (FastAPI + Gemini)

## Project Structure

```
.
├── .env
├── README.md
├── requirements.txt
└── app
    ├── __init__.py
    ├── config.py
    ├── main.py
    ├── schemas.py
    └── services
        ├── gemini.py
        └── telegram.py
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:

```env
TELEGRAM_TOKEN=
GEMINI_API_KEY=
```

## Run Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configure Telegram Webhook

Replace `<PUBLIC_URL>` with your HTTPS URL:

```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=<PUBLIC_URL>/webhook/<TELEGRAM_TOKEN>"
```

## Verify Webhook

Open:

```
GET /webhook/<TELEGRAM_TOKEN>
```

or:

```bash
curl "http://localhost:8000/webhook/<TELEGRAM_TOKEN>"
```

## Test

Send a message to your Telegram bot. The bot will parse intent via Gemini and reply:
- `Task added: ...`
- `Event scheduled: ...`

