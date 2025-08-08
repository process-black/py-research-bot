# Python Bolt Slack Bot - Claude Context

## Key Commands & Setup

### Virtual Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run Socket Mode app
python3 app.py

# Run HTTP Mode app (Flask)
python3 server.py
```

### Production Commands
```bash
# Deploy to Heroku (Socket Mode)
heroku create your-app-name
heroku buildpacks:set heroku/python
heroku config:set SLACK_BOT_TOKEN=... SLACK_APP_TOKEN=...
git add . && git commit -m "init" && git push heroku main
heroku ps:scale worker=1

# Deploy to Heroku (HTTP Mode)
heroku config:set SLACK_BOT_TOKEN=... SLACK_SIGNING_SECRET=...
heroku ps:scale web=1
```

## Environment Variables

### Socket Mode (Recommended for development)
- `SLACK_BOT_TOKEN=xoxb-***` (required)
- `SLACK_APP_TOKEN=xapp-***` (required, needs `connections:write` scope)

### HTTP Mode (Production)
- `SLACK_BOT_TOKEN=xoxb-***` (required)
- `SLACK_SIGNING_SECRET=***` (required)

## Project Structure Options

### Socket Mode Files
- `requirements.txt` - dependencies
- `app.py` - main application
- `Procfile` - for Heroku deployment
- `runtime.txt` - Python version (optional)

### HTTP Mode Files  
- `requirements.txt` - dependencies (includes flask, gunicorn)
- `server.py` - Flask application
- `Procfile` - for Heroku deployment
- `runtime.txt` - Python version (optional)

## Key Differences from Node.js
- Use `requirements.txt` instead of `package.json`
- Use `venv` instead of `nvm`/`pnpm`
- Use decorators (`@app.message()`) instead of listeners
- Use `gunicorn` for production instead of node/pm2
- Choose sync `App` or async `AsyncApp`

## OpenAI Integration

### CRITICAL: ONLY Use Responses API
**⚠️ NEVER use Chat Completions API (`chat.completions.create`) in this project.**

We use OpenAI's **Responses API EXCLUSIVELY** for all OpenAI interactions:
- ✅ PDF file processing
- ✅ Structured outputs with Pydantic models  
- ✅ GPT-5, GPT-4o, GPT-4o-mini support
- ✅ File uploads and references

**Once set up with Responses API, NEVER switch back to Completions API.**

```python
# Upload file
file_upload = client.files.create(
    file=open(pdf_path, 'rb'),
    purpose='user_data'
)

# Use Responses API with structured output
response = client.responses.parse(
    model="gpt-5",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": file_upload.id
                },
                {
                    "type": "input_text",
                    "text": "Extract structured metadata from this PDF..."
                }
            ]
        }
    ],
    text_format=PDFMetadata  # Pydantic model for structured output
)

# Get structured result and cleanup
metadata = response.output_parsed  # Direct access to Pydantic model
client.files.delete(file_upload.id)
```

**Why Responses API Only:**
- PDF file support with GPT-5
- Structured outputs work correctly
- Consistent API across all models
- No mixing of incompatible APIs

## Architecture Guidelines

### Utils Directory (`src/utils/`)
**Purpose**: Contains only abstract, reusable utilities that could be used in ANY Python project.

**Rules:**
- ❌ **NO project-specific logic** - utils should never "feel" specific to this Slack bot
- ❌ **NO business rules** - no PDF-specific validation, no Slack-specific formatting
- ❌ **NO domain knowledge** - no knowledge of "PDFs", "research papers", "Slack channels"
- ✅ **Generic operations only** - database clients, API wrappers, file helpers, logging
- ✅ **Reusable across projects** - should work in a web app, CLI tool, or different bot

**Examples:**
```python
# ✅ GOOD - Generic Airtable client
class AirtableClient:
    def create_record(self, base_id, table_name, fields):
        # Pure CRUD operation

# ❌ BAD - PDF-specific in utils
class AirtableClient:
    def save_pdf_metadata(self, title, topic, study_type):
        # This belongs in a bot, not utils
```

### Handlers Directory (`src/handlers/`)
**Purpose**: Abstract Slack event routing and message processing.

**Contains:**
- Event listeners (`@app.event`, `@app.message`)
- Routing logic (which bot handles what)
- Slack-specific utilities (thread detection, channel management)
- Generic message formatting

### Bots Directory (`src/bots/`)
**Purpose**: All business logic and domain-specific operations.

**Contains:**
- Feature-specific workflows (PDF processing, research analysis)
- Domain validation (valid topics, study types)
- Business rules and logic
- Integration orchestration (OpenAI + Airtable + Slack)