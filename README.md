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
Create a `.env` file in the project root with the following variables:
```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_BOT_USER_TOKEN=xoxp-your-user-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret

# Slack Channels (Hardcoded for now--do something more impressive as you build this out)
SLACK_LOGGING_CHANNEL=your-logging-channel-id
SLACK_ACADEMIC_ARTICLES_CHANNEL=your-articles-channel-id

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-openai-key

# Airtable Configuration
AIRTABLE_API_TOKEN=pat-your-airtable-token
AIRTABLE_AI_TEACHING_AND_LEARNING_BASE=app-your-base-id
AIRTABLE_PDFS_TABLE_ID=tbl-your-table-id
AIRTABLE_PDFS_VIEW_ID=viw-your-view-id
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
   - `reactions:read`
   - `files:read`
3. Enable Socket Mode under "Socket Mode"
4. Create an App-Level Token with `connections:write` scope
5. Install the app to your workspace

## Environment Variables

### Required for Development
All variables must be configured in your `.env` file:

**Slack Configuration:**
- `SLACK_BOT_TOKEN` - Your bot's OAuth token (starts with `xoxb-`)
- `SLACK_BOT_USER_TOKEN` - Your user OAuth token (starts with `xoxp-`)
- `SLACK_APP_TOKEN` - Your app-level token for Socket Mode (starts with `xapp-`)
- `SLACK_SIGNING_SECRET` - Your app's signing secret for request verification

**Slack Channels:**
- `SLACK_LOGGING_CHANNEL` - Channel ID for logging messages
- `SLACK_ACADEMIC_ARTICLES_CHANNEL` - Channel ID for academic article processing

**External APIs:**
- `OPENAI_API_KEY` - OpenAI API key for GPT models (starts with `sk-proj-`)
- `AIRTABLE_API_TOKEN` - Airtable personal access token (starts with `pat`)
- `AIRTABLE_AI_TEACHING_AND_LEARNING_BASE` - Airtable base ID (starts with `app`)
- `AIRTABLE_PDFS_TABLE_ID` - Airtable table ID for PDFs table (starts with `tbl`)
- `AIRTABLE_PDFS_VIEW_ID` - Airtable view ID for default view (starts with `viw`)

**⚠️ Production Note:** The above environment variables are hardcoded for development purposes only. In production environments serving multiple Slack workspaces, implement a more robust configuration system such as:
- Database-driven configuration per workspace
- Dynamic table/view discovery via Airtable API
- Workspace-specific environment variable patterns
- Configuration management services (AWS Systems Manager, Azure Key Vault, etc.)

## Features

- Responds to "hello" messages
- Shows help with "help" command
- Runs in Socket Mode (no public URL needed)

## Development

The bot uses Socket Mode, which means:
- No need for a public URL or webhook endpoints
- Perfect for local development
- Works great on Heroku with a worker dyno