# Python Research Bot

A Slack bot built with Python using Slack's Bolt framework in Socket Mode.

## Quick Start

1. **Set up virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your actual Slack tokens
```

4. **Run the bot:**
```bash
python3 app.py
```

## Slack App Setup

1. Create a new Slack app at https://api.slack.com/apps
2. Add these OAuth scopes under "OAuth & Permissions":
   - `chat:write`
   - `app_mentions:read`
   - `channels:history`
   - `im:history`
3. Enable Socket Mode under "Socket Mode"
4. Create an App-Level Token with `connections:write` scope
5. Install the app to your workspace

## Environment Variables

- `SLACK_BOT_TOKEN` - Your bot's OAuth token (starts with `xoxb-`)
- `SLACK_APP_TOKEN` - Your app-level token for Socket Mode (starts with `xapp-`)

## Features

- Responds to "hello" messages
- Shows help with "help" command
- Runs in Socket Mode (no public URL needed)

## Development

The bot uses Socket Mode, which means:
- No need for a public URL or webhook endpoints
- Perfect for local development
- Works great on Heroku with a worker dyno