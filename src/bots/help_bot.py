"""Help Bot - provides help information and commands."""

from src.bots.base_bot import BaseBot


class HelpBot(BaseBot):
    """Bot that provides help information and available commands."""
    
    def handle_message(self, message, say):
        """Process help request and provide information."""
        user_id = message.get('user')
        self.log(f"Providing help to user: {user_id}")
        
        help_text = """
        Hi! I'm a Python research bot. Here's what I can do:
        
        • Say "hello" - I'll greet you
        • Say "help" - Show this help message
        • Upload a PDF - I'll summarize it!
        
        More features coming soon!
        """
        
        say(help_text)