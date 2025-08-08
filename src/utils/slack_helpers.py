"""Slack utility functions and helpers."""


def is_pdf_file(file_info):
    """Check if uploaded file is a PDF."""
    return (
        file_info.get('mimetype') == 'application/pdf' or
        file_info.get('name', '').lower().endswith('.pdf')
    )


def get_channel_name(client, channel_id):
    """Get channel name from channel ID."""
    try:
        response = client.conversations_info(channel=channel_id)
        return response['channel']['name']
    except Exception as e:
        print(f"Error getting channel name: {e}")
        return channel_id


def send_startup_message(client, channel_id, bot_name="Python Research Bot"):
    """Send startup message to specified channel."""
    try:
        client.chat_postMessage(
            channel=channel_id,
            text=f"🤖 {bot_name} is starting up!"
        )
        return True
    except Exception as e:
        print(f"Failed to send startup message: {e}")
        return False