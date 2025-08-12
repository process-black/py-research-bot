"""Event handlers for file uploads, reactions, etc."""

from src.bots.pdf_summarizer import PDFSummarizerBot
from src.utils import colored_logs as llog


def register_event_handlers(app):
    """Register all event handlers."""
    
    @app.event("app_mention")
    def handle_app_mention(event, say):
        """Handle when bot is @mentioned."""
        llog.magenta("📢 APP MENTION EVENT:")
        llog.blue(event)
        
        # Extract text after the mention
        text = event.get('text', '').lower()
        
        if 'hello' in text or 'hi' in text:
            say(f"Hey there <@{event['user']}>!")
        elif 'help' in text:
            say("Hi! Try DMing me 'help' for a full list of commands!")
        else:
            say("Hi! Try DMing me for more features, or say 'help' here!")
    
    @app.event("file_shared")
    def handle_file_shared(event, client):
        """Handle file upload events and route to appropriate bots."""
        llog.cyan("📁 FILE SHARED EVENT:")
        llog.blue(event)
        
        try:
            # Get detailed file info from Slack API
            file_id = event.get("file_id")
            channel_id = event.get("channel_id")
            
            if not file_id:
                llog.red("❌ No file_id in file_shared event")
                return
            
            # Get full file details from Slack
            file_info = client.files_info(file=file_id)
            file_data = file_info.get("file", {})
            
            llog.yellow("📋 File details:")
            llog.blue(file_data)
            
            # Get the message timestamp from the file shares info
            thread_ts = None
            shares = file_data.get("shares", {})
            if shares and "public" in shares and channel_id in shares["public"]:
                # Get the message timestamp from the first share in this channel
                share_info = shares["public"][channel_id][0]
                thread_ts = share_info.get("ts")
                llog.cyan(f"📍 Found message timestamp for thread: {thread_ts}")
            
            # Check if it's a PDF
            file_name = file_data.get("name", "")
            mimetype = file_data.get("mimetype", "")
            
            if mimetype == "application/pdf" or file_name.lower().endswith(".pdf"):
                llog.green(f"🔍 PDF detected: {file_name}")
                
                # Initialize and run PDF summarizer bot with thread context
                pdf_bot = PDFSummarizerBot(slack_client=client)
                pdf_bot.process_file(file_data, channel_id, thread_ts=thread_ts)
            else:
                llog.gray(f"⏭️ Skipping non-PDF file: {file_name} (type: {mimetype})")
                
        except Exception as e:
            llog.red(f"❌ Error handling file_shared event: {str(e)}")
            llog.blue(f"Event data: {event}")
    
    @app.event("file_public")
    def handle_file_public(event):
        """Handle file made public events (ignored for now)."""
        llog.gray("📄 File made public (ignored)")
    
    @app.event("file_created") 
    def handle_file_created(event):
        """Handle file created events (ignored for now)."""
        llog.gray("📄 File created (ignored)")
    
    @app.event({"type": "message", "subtype": "file_share"})
    def handle_file_share_message(event):
        """Handle file share message events (ignored - handled by file_shared)."""
        llog.gray("💬 File share message (ignored - handled by file_shared event)")
    
    @app.event({"type": "message", "subtype": "channel_join"})
    def handle_channel_join_message(event):
        """Handle channel join message events (ignored)."""
        llog.gray("👋 Channel join message (ignored)")
    
    @app.event("reaction_added")
    def handle_reaction_added(event, client):
        """Handle emoji reactions - trigger PDF processing on books emoji."""
        try:
            reaction = event.get("reaction", "")
            user = event.get("user", "")
            channel = event.get("item", {}).get("channel")
            timestamp = event.get("item", {}).get("ts")
            
            llog.cyan(f"🎭 REACTION ADDED: {reaction} by user {user}")
            
            # Only process books emoji reactions
            if reaction != "books":
                llog.gray(f"⏭️ Ignoring non-books reaction: {reaction}")
                return
            
            llog.green(f"📚 Books emoji detected! Processing message in {channel} at {timestamp}")
            
            # Get the original message to check for PDFs
            try:
                message_response = client.conversations_history(
                    channel=channel,
                    latest=timestamp,
                    limit=1,
                    inclusive=True
                )
                
                messages = message_response.get("messages", [])
                if not messages:
                    llog.yellow("⚠️ Could not retrieve original message")
                    return
                
                original_message = messages[0]
                llog.blue(f"📝 Original message: {original_message}")
                
                # Check if message has PDF files
                files = original_message.get("files", [])
                pdf_files = []
                
                for file_data in files:
                    file_name = file_data.get("name", "")
                    mimetype = file_data.get("mimetype", "")
                    
                    if mimetype == "application/pdf" or file_name.lower().endswith(".pdf"):
                        pdf_files.append(file_data)
                        llog.green(f"🔍 Found PDF in reacted message: {file_name}")
                
                # Process each PDF file
                if pdf_files:
                    pdf_bot = PDFSummarizerBot(slack_client=client)
                    
                    for file_data in pdf_files:
                        llog.magenta(f"🔄 Processing PDF from books reaction: {file_data.get('name', 'Unknown')}")
                        # Use the original message timestamp as thread_ts to reply in thread
                        pdf_bot.process_file(file_data, channel, thread_ts=timestamp)
                else:
                    llog.yellow("📚 Books reaction added but no PDF files found in message")
                    
            except Exception as e:
                llog.red(f"❌ Error retrieving message for reaction: {str(e)}")
                
        except Exception as e:
            llog.red(f"❌ Error handling reaction_added event: {str(e)}")
            llog.blue(f"Event data: {event}")