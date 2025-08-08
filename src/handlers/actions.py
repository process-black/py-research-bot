"""Action handlers for buttons, slash commands, etc."""


def register_action_handlers(app):
    """Register all action handlers."""
    
    @app.action("button_click")
    def handle_button_click(ack, body, client):
        """Handle button click actions."""
        ack()
        # TODO: Route to appropriate bots based on action
        print(f"Button clicked: {body}")