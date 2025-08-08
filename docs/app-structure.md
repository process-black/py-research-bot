# Application Structure

## Overview

This Python Slack bot follows a modular architecture with clear separation of concerns, similar to a typical Node.js project structure.

## Directory Structure

```
src/
├── handlers/          # Slack event listeners and routing
│   ├── __init__.py
│   ├── messages.py    # Message event handlers
│   ├── events.py      # File uploads, reactions, etc.
│   └── actions.py     # Button clicks, slash commands
├── bots/              # Specialized agents/workers
│   ├── __init__.py
│   ├── pdf_summarizer.py    # PDF → OpenAI → Slack + Airtable
│   ├── research_bot.py      # Academic paper analysis
│   └── base_bot.py          # Base class for common functionality
└── utils/             # Shared utilities and integrations
    ├── __init__.py
    ├── openai_client.py     # OpenAI API wrapper
    ├── airtable_client.py   # Airtable integration
    ├── slack_helpers.py     # Common Slack operations
    └── logging.py           # Structured logging setup
```

## Flow

1. **Handlers** receive Slack events (messages, file uploads, etc.)
2. **Handlers** analyze the event (channel, content, file type, etc.)
3. **Handlers** route to appropriate **Bots** based on routing logic
4. **Bots** perform specialized work using **Utils**
5. **Bots** send results back to Slack and external services

## Example Flow: PDF Summary Bot

1. `handlers/events.py` detects file upload event
2. Checks if file type is PDF
3. Routes to `bots/pdf_summarizer.py`
4. Bot uses `utils/openai_client.py` to summarize PDF
5. Bot uses `utils/airtable_client.py` to store results
6. Bot uses `utils/slack_helpers.py` to post summary to Slack

## Benefits

- **Modularity**: Each bot handles one specific task
- **Reusability**: Utils can be shared across bots
- **Testability**: Each component can be tested independently
- **Scalability**: Easy to add new bots and handlers
- **Maintainability**: Clear separation of concerns