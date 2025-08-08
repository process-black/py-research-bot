"""Base class for all bots."""

class BaseBot:
    """Base class providing common functionality for all bots."""
    
    def __init__(self, slack_client=None):
        """Initialize bot with Slack client."""
        self.slack_client = slack_client
        
    def log(self, message, level="info"):
        """Log message (placeholder for structured logging)."""
        print(f"[{level.upper()}] {self.__class__.__name__}: {message}")
        
    def send_to_channel(self, channel, text):
        """Send message to Slack channel."""
        if self.slack_client:
            return self.slack_client.chat_postMessage(
                channel=channel,
                text=text
            )