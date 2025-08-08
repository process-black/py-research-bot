"""Hello Bot - handles greeting messages."""

from src.bots.base_bot import BaseBot


class HelloBot(BaseBot):
    """Bot that handles hello/greeting messages."""
    
    def handle_message(self, message, say):
        """Process hello message and respond with greeting."""
        user_id = message.get('user')
        self.log(f"Greeting user: {user_id}")
        
        say(f"Hey there <@{user_id}>!")