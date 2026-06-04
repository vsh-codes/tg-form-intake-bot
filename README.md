# Telegram Form Intake Bot

Production-ready Telegram bot for collecting structured applications and syncing them to Google Sheets in real time.

Built for businesses that need to capture leads, applications, or onboarding data through Telegram — without paying for SaaS form builders or maintaining custom intake forms.

![Python](https://img.shields.io/badge/python-3.12-blue)
![aiogram](https://img.shields.io/badge/aiogram-3.13-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)

---

## Why this exists

Most businesses that need to collect applications via Telegram end up with one of three bad options:

1. **Manual chat** — admin reads messages, copies data to a spreadsheet, misses entries
2. **Google Forms link** — friction, fewer completions, no Telegram-native experience
3. **No-code bot builders** — $30–80/mo recurring, vendor lock-in, hard to customize

This bot replaces all three. Self-hosted, $0/mo running cost (besides VPS), full control over the flow.

---

## What it does

- **Multi-step form intake** with FSM-based state management (no lost answers if user pauses)
- **Input validation** — email, phone, required fields, custom regex per field
- **Google Sheets sync** — every submission appended to your sheet in real time
- **Admin notifications** — owner gets a Telegram message for every new application
- **Local SQLite cache** — deduplication, draft recovery, offline resilience
- **/admin command** — quick stats: total submissions, today, this week
- **Cancellation flow** — users can abort mid-form, state cleared cleanly
- **Production logging** — structured logs via Loguru, ready for shipping to any aggregator

---

## Real-world use cases

| Industry | Use case |
|----------|----------|
| **HR / Recruiting** | Application intake for job openings |
| **Real Estate** | Property viewing requests with contact + preferences |
| **Education** | Course enrollment with prerequisites check |
| **Event Management** | Registration with ticket type, dietary requirements |
| **B2B SaaS** | Demo request with company size, role, use case |
| **Local Services** | Booking requests (clinics, salons, consultations) |

---

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌──────────────────┐
│  Telegram   │───▶│  aiogram 3   │───▶│  Form Handlers   │
│   Users     │    │  (long poll) │    │  (FSM-based)     │
└─────────────┘    └──────────────┘    └────────┬─────────┘
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          ▼                     ▼                     ▼
                  ┌───────────────┐    ┌────────────────┐    ┌────────────────┐
                  │  Validators   │    │  SQLite Cache  │    │  Google Sheets │
                  │  (per field)  │    │  (dedup +      │    │  (primary      │
                  │               │    │   drafts)      │    │   storage)     │
                  └───────────────┘    └────────────────┘    └────────────────┘
                                                                     │
                                                                     ▼
                                                            ┌────────────────┐
                                                            │  Admin TG      │
                                                            │  Notification  │
                                                            └────────────────┘
```

---

## Tech stack

- **Python 3.12** — async-first
- **aiogram 3** — modern Telegram framework with FSM, routers, filters
- **Pydantic Settings** — typed environment config, fail-fast on missing vars
- **gspread + google-auth** — Google Sheets API via service account
- **aiosqlite** — async SQLite for local storage
- **Loguru** — structured logging with rotation
- **Docker + docker-compose** — one-command deployment

---

## Quick start

### 1. Prerequisites

- Python 3.12+ (or just Docker)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A Google Sheet + service account with Editor access ([guide below](#google-sheets-setup))
- Your Telegram user ID for admin notifications (get from [@userinfobot](https://t.me/userinfobot))

### 2. Clone and configure

```bash
git clone https://github.com/vsh-codes/tg-form-intake-bot.git
cd tg-form-intake-bot
cp .env.example .env
# Edit .env with your tokens, sheet ID, admin chat ID
```

### 3. Run (option A: Docker, recommended)

```bash
docker compose up -d
docker compose logs -f
```

### 4. Run (option B: local Python)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m main
```

That's it. Send `/start` to your bot.

---

## Google Sheets setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → create a project
2. Enable **Google Sheets API** and **Google Drive API**
3. Create a **Service Account** under IAM & Admin
4. Generate a JSON key, save as `credentials/service-account.json`
5. Open your Google Sheet, share it with the service account email (Editor access)
6. Copy the sheet ID from the URL (the long string between `/d/` and `/edit`)
7. Paste the sheet ID into `.env` as `GOOGLE_SHEET_ID`

The first row of your sheet should match the field names defined in `bot/states.py` (default: `timestamp, username, full_name, email, phone, message`).

---

## Customizing the form

All form questions, validation rules, and messages are configured in three files:

- `bot/states.py` — define the FSM states (one per question)
- `bot/handlers.py` — handler logic per state
- `bot/messages.py` — all user-facing text strings (for easy translation / rewording)
- `bot/validators.py` — per-field validation logic

Adding a new field takes about 5 minutes — see the inline comments in `bot/states.py`.

---

## Configuration

All settings live in `.env` (see `.env.example` for the full template):

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | yes | Telegram bot token from @BotFather |
| `ADMIN_CHAT_ID` | yes | Your Telegram user ID (numeric) |
| `GOOGLE_SHEET_ID` | yes | Target Google Sheet ID |
| `GOOGLE_SERVICE_ACCOUNT_PATH` | yes | Path to service account JSON |
| `DATABASE_PATH` | no | SQLite file path (default: `data/bot.db`) |
| `LOG_LEVEL` | no | DEBUG / INFO / WARNING / ERROR (default: INFO) |

---

## Project structure

```
tg-form-intake-bot/
├── bot/
│   ├── handlers.py       # All command and state handlers
│   ├── states.py         # FSM state definitions
│   ├── keyboards.py      # Inline & reply keyboards
│   ├── messages.py       # User-facing text strings
│   └── validators.py     # Input validation logic
├── services/
│   ├── sheets.py         # Google Sheets API integration
│   └── notifications.py  # Admin notification logic
├── db/
│   └── storage.py        # SQLite storage layer
├── credentials/
│   └── service-account.json   # (gitignored)
├── data/
│   └── bot.db            # (gitignored)
├── config.py             # Pydantic Settings
├── main.py               # Entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env                  # (gitignored)
```

---

## Deployment

The bot is designed to run 24/7 on any small VPS (Hetzner, DigitalOcean, AWS Lightsail). It uses long polling, so no public IP or webhook setup needed.

**Resource footprint:** ~50–80 MB RAM, negligible CPU. Runs comfortably on a $4/mo VPS.

For production:
- Set up a `systemd` unit (or use `docker compose` with `restart: unless-stopped` — already in the included compose file)
- Mount `data/` and `credentials/` as volumes so they survive container rebuilds
- Forward logs to your aggregator of choice (the Loguru sink in `main.py` can be swapped for a network sink)

---

## Roadmap

Planned features (open to PRs):

- [ ] Webhook mode for higher throughput
- [ ] Multi-language support (currently English, structure ready for i18n)
- [ ] Built-in spam detection (rate limiting per user)
- [ ] Optional CRM integrations (HubSpot, Pipedrive)
- [ ] Admin web dashboard for stats and submission browsing
- [ ] File attachment support (photos, documents)

---

## License

MIT — see [LICENSE](LICENSE). Free to use, modify, and deploy commercially.

---

## Contact

Built and maintained by [vsh](https://github.com/vsh-codes).

Available for custom Telegram bot development, AI integrations, and business automation work — [Upwork profile](https://www.upwork.com/freelancers/~01valerii) (placeholder, update with real URL).

For questions or feature requests, open an issue.
