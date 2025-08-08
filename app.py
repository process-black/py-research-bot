import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from src.handlers.messages import register_message_handlers
from src.handlers.events import register_event_handlers
from src.handlers.actions import register_action_handlers
from src.utils.slack_helpers import send_startup_message

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Register all handlers
register_message_handlers(app)
register_event_handlers(app)
register_action_handlers(app)

if __name__ == "__main__":
    # Ensure /tmp directory exists (for Heroku compatibility)
    import os
    os.makedirs('/tmp', exist_ok=True)
    print("✅ /tmp directory ready")
    
    # Debug environment variables
    openai_key = os.environ.get("OPENAI_API_KEY")
    print(f"🔑 OpenAI API Key loaded: {'✅' if openai_key else '❌'}")
    if openai_key:
        print(f"🔑 Key preview: {openai_key[:10]}...")
    
    # Send startup message to logging channel
    logging_channel = os.environ.get("SLACK_LOGGING_CHANNEL")
    if logging_channel:
        success = send_startup_message(app.client, logging_channel, "Python Research Bot")
        if success:
            print(f"Startup message sent to channel: {logging_channel}")
    
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()