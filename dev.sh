#!/bin/bash

# Activate virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    source .venv/bin/activate
fi

# Run app with auto-restart
watchfiles 'python app.py' .