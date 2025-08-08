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

### Using Responses API (Modern Approach)
We use OpenAI's Responses API for PDF analysis, not the older Assistants API.

```python
# Upload file
file_upload = client.files.create(
    file=open(pdf_path, 'rb'),
    purpose='user_data'
)

# Use Responses API with file variable
response = client.responses.create(
    model="gpt-4o-mini",
    prompt={
        "id": "pdf_analysis_prompt",
        "variables": {
            "document": {
                "type": "input_file",
                "file_id": file_upload.id,
            },
            "template": "Analysis template here..."
        },
        "content": "Analyze the document according to template."
    }
)

# Get result and cleanup
summary = response.output_text
client.files.delete(file_upload.id)
```

**Benefits:**
- Single API call (no polling/waiting)
- Direct file variables in prompts
- Automatic cleanup
- Simpler than Assistants API