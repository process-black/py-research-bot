"""Message event handlers for Slack bot."""

import os
from src.bots.hello_bot import HelloBot
from src.bots.help_bot import HelpBot
from src.utils import colored_logs as llog


def register_message_handlers(app):
    """Register all message event handlers."""
    
    # Initialize bots
    hello_bot = HelloBot(slack_client=app.client)
    help_bot = HelpBot(slack_client=app.client)
    
    # Get logging channel for centralized logging
    logging_channel = os.environ.get("SLACK_LOGGING_CHANNEL")
    
    @app.message()
    def route_messages(message, say):
        """Route messages to appropriate bots based on content."""
        text = message.get('text', '').lower().strip()
        user_id = message.get('user')
        
        # Skip app mentions - they're handled by the app_mention event handler
        if text.startswith('<@u099dps5s4t>'):  # Your bot's user ID
            llog.gray("→ Skipping app mention (handled by app_mention event)")
            return
        
        # Debug: Log the full message payload for non-mentions
        llog.cyan("📥 DM/CHANNEL MESSAGE EVENT:")
        llog.blue(message)
        llog.divider()
        
        # Route to specific bots based on message content
        if 'hello' in text or 'hi' in text:
            llog.green(f"→ Routing to HelloBot: '{text}'")
            hello_bot.handle_message(message, say)
            # Centralized logging
            if logging_channel:
                app.client.chat_postMessage(
                    channel=logging_channel,
                    text=f"HelloBot greeted user <@{user_id}>"
                )
        elif 'help' in text:
            llog.green(f"→ Routing to HelpBot: '{text}'")
            help_bot.handle_message(message, say)
            # Centralized logging
            if logging_channel:
                app.client.chat_postMessage(
                    channel=logging_channel,
                    text=f"HelpBot assisted user <@{user_id}>"
                )
        else:
            # Log unrecognized messages but don't respond
            llog.yellow(f"→ Unrecognized message: '{text}' from user {user_id}")