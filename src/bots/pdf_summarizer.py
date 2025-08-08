"""PDF Summarizer Bot - processes PDF files and creates summaries."""

import os
from src.bots.base_bot import BaseBot
from src.utils.openai_client import OpenAIClient
from src.utils.airtable_client import AirtableClient
from src.utils.pdf_helpers import download_pdf_from_slack, extract_text_from_pdf, cleanup_temp_file
from src.utils import colored_logs as llog


class PDFSummarizerBot(BaseBot):
    """Bot that summarizes PDF files using OpenAI and stores results."""
    
    def __init__(self, slack_client=None):
        """Initialize with OpenAI and Airtable clients."""
        super().__init__(slack_client)
        self.openai_client = OpenAIClient()
        self.airtable_client = AirtableClient()
        self.bot_token = os.environ.get("SLACK_BOT_TOKEN")
    
    def process_file(self, file_info, channel_id, thread_ts=None):
        """Process uploaded PDF file through the full workflow."""
        file_name = file_info.get('name', 'Unknown')
        file_url = file_info.get('url_private_download')
        
        llog.magenta(f"🔄 Starting PDF processing workflow: {file_name}")
        if thread_ts:
            llog.gray(f"📝 Will reply to thread: {thread_ts}")
        
        temp_file_path = None
        try:
            # Step 1: Download PDF to temp folder
            temp_file_path = download_pdf_from_slack(file_url, self.bot_token)
            if not temp_file_path:
                self.send_error_to_channel(channel_id, "Failed to download PDF file")
                return
            
            # Step 2: Extract structured metadata from PDF
            llog.yellow("🤖 Extracting PDF metadata...")
            metadata_result = self.openai_client.extract_pdf_metadata(temp_file_path, file_name)
            
            # Step 3: Log the metadata extraction result (excluding large data)
            llog.green("📊 Metadata Extraction Result:")
            # Create a safe version for logging (exclude large binary data)
            safe_result = {k: v for k, v in metadata_result.items() if k != "metadata" or not isinstance(v, dict) or len(str(v)) < 1000}
            if metadata_result.get("metadata") and len(str(metadata_result["metadata"])) >= 1000:
                safe_result["metadata"] = "[Large metadata object - suppressed from logs]"
            llog.blue(safe_result)
            llog.divider()
            
            if metadata_result["success"]:
                metadata = metadata_result["metadata"]
                
                # Step 4: Save to Airtable
                try:
                    llog.yellow("🗃️ Saving to Airtable...")
                    airtable_record = self.save_pdf_to_airtable(metadata, temp_file_path)
                    
                    llog.green(f"✅ Saved to Airtable: {airtable_record['id']}")
                    
                    # Step 5: Send results to Slack
                    self.send_metadata_to_channel(channel_id, file_name, metadata, airtable_record, thread_ts=thread_ts)
                    llog.green(f"✅ PDF processing completed successfully: {file_name}")
                    
                except Exception as airtable_error:
                    llog.red(f"❌ Airtable save failed: {str(airtable_error)}")
                    # Still send to Slack even if Airtable fails
                    self.send_metadata_to_channel(channel_id, file_name, metadata, None, thread_ts=thread_ts)
                    
            else:
                self.send_error_to_channel(channel_id, f"Metadata extraction failed: {metadata_result.get('error', 'Unknown error')}", thread_ts=thread_ts)
                
        except Exception as e:
            llog.red(f"❌ PDF processing failed: {str(e)}")
            self.send_error_to_channel(channel_id, f"Processing failed: {str(e)}", thread_ts=thread_ts)
        
        finally:
            # Step 6: Always cleanup temp file
            if temp_file_path:
                cleanup_temp_file(temp_file_path)
    
    def save_pdf_to_airtable(self, metadata: dict, pdf_file_path: str) -> dict:
        """
        Save PDF metadata and file to Airtable with PDF-specific field mapping.
        
        Args:
            metadata: Extracted PDF metadata
            pdf_file_path: Path to PDF file
            
        Returns:
            dict: Created Airtable record
        """
        base_id = os.environ.get("AIRTABLE_AI_TEACHING_AND_LEARNING_BASE")
        if not base_id:
            raise ValueError("AIRTABLE_AI_TEACHING_AND_LEARNING_BASE environment variable not set")
        
        # PDF-specific field mapping (without file attachment)
        fields = {
            "Title": metadata["title"],
            "Topic": self.validate_topic(metadata["topic"]), 
            "StudyType": self.validate_study_type(metadata["study_type"]),
            "Summary": metadata["summary"]
        }
        
        # Add optional fields
        if metadata.get("year"):
            fields["Year"] = metadata["year"]
        if metadata.get("link"):
            fields["Link"] = metadata["link"]
        
        # Create the record first (without file attachment)
        record = self.airtable_client.create_record(base_id, "PDFs", fields)
        
        # Then upload PDF file as attachment to the created record
        if pdf_file_path and os.path.exists(pdf_file_path):
            llog.yellow(f"📎 Uploading PDF file: {os.path.basename(pdf_file_path)}")
            try:
                updated_record = self.airtable_client.upload_attachment_to_record(
                    base_id, "PDFs", record["id"], "File", pdf_file_path
                )
                return updated_record
            except Exception as e:
                llog.yellow(f"⚠️ Record created but file upload failed: {str(e)}")
                # Return the record even if file upload fails
                return record
        
        return record
    
    def validate_topic(self, topic: str) -> str:
        """Validate and normalize topic value for PDF records."""
        valid_topics = [
            "Learning outcomes",
            "Tool development", 
            "Professional practice",
            "Student perspectives",
            "User experience and interaction",
            "Theoretical background",
            "AI literacy",
            "Other"
        ]
        
        # Try exact match first
        if topic in valid_topics:
            return topic
            
        # Try case-insensitive match
        topic_lower = topic.lower()
        for valid_topic in valid_topics:
            if topic_lower == valid_topic.lower():
                return valid_topic
                
        # Default to "Other" if no match
        llog.yellow(f"⚠️ Unknown topic '{topic}', defaulting to 'Other'")
        return "Other"
    
    def validate_study_type(self, study_type: str) -> str:
        """Validate and normalize study type value for PDF records."""
        valid_types = [
            "Review",
            "Experimental", 
            "Quantitative",
            "Qualitative",
            "Mixed-methods",
            "Observational"
        ]
        
        # Try exact match first
        if study_type in valid_types:
            return study_type
            
        # Try case-insensitive match
        type_lower = study_type.lower()
        for valid_type in valid_types:
            if type_lower == valid_type.lower():
                return valid_type
                
        # Default to "Review" if no match
        llog.yellow(f"⚠️ Unknown study type '{study_type}', defaulting to 'Review'")
        return "Review"
    
    def analyze_pdf_with_openai(self, pdf_file_path):
        """
        Analyze PDF using OpenAI's Responses API with our specific summarization prompt.
        
        Args:
            pdf_file_path (str): Path to PDF file
            
        Returns:
            dict: Analysis response from OpenAI
        """
        
        try:
            llog.yellow("🤖 Uploading PDF to OpenAI using Responses API...")
            
            # Upload PDF file to OpenAI
            with open(pdf_file_path, 'rb') as pdf_file:
                file_upload = self.openai_client.client.files.create(
                    file=pdf_file,
                    purpose='user_data'
                )
            
            llog.cyan(f"📤 PDF uploaded to OpenAI: {file_upload.id}")
            
            # Our specific summarization prompt
            summary_prompt = """
Please analyze this PDF document and provide a structured summary:

**DOCUMENT SUMMARY:**
- **Main Topic**: [Brief description of the document's primary focus]
- **Key Points**: [3-5 bullet points of the most important information]
- **Document Type**: [Research paper, report, manual, etc.]
- **Target Audience**: [Who this document is intended for]
- **Key Takeaways**: [2-3 actionable insights or conclusions]

**TECHNICAL DETAILS** (if applicable):
- **Methodology**: [Research methods, approaches used]
- **Data/Evidence**: [Key statistics, findings, or evidence presented]
- **Tools/Technologies**: [Any specific tools, technologies, or frameworks mentioned]

**RELEVANCE ASSESSMENT:**
- **Academic Value**: [High/Medium/Low - why?]
- **Practical Applications**: [How can this be applied?]
- **Related Topics**: [What other areas does this connect to?]
            """
            
            # Try GPT-5 first, fallback to GPT-4o if needed
            models_to_try = ["gpt-5", "gpt-4o", "gpt-4o-mini"]
            response = None
            model_used = None
            
            for model in models_to_try:
                try:
                    llog.yellow(f"🎯 Trying model: {model}")
                    
                    # Create client with timeout for this request
                    from openai import OpenAI
                    timeout_client = OpenAI(
                        api_key=self.openai_client.client.api_key,
                        timeout=180.0  # 3 minute timeout
                    )
                    
                    response = timeout_client.responses.create(
                        model=model,
                        input=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "input_file",
                                        "file_id": file_upload.id,
                                    },
                                    {
                                        "type": "input_text",
                                        "text": summary_prompt,
                                    }
                                ]
                            }
                        ]
                    )
                    
                    model_used = model
                    llog.green(f"✅ Success with {model}")
                    break
                    
                except Exception as e:
                    error_msg = str(e)
                    llog.yellow(f"❌ {model} failed: {error_msg}")
                    
                    # Skip to GPT-4o-mini if GPT-5 is not available
                    if "does not exist" in error_msg.lower() or "not found" in error_msg.lower():
                        llog.yellow(f"⏭️ {model} not available, skipping to next model")
                    
                    if model == models_to_try[-1]:  # Last model
                        raise e
                    continue
            
            # Cleanup uploaded file if we want
            self.openai_client.client.files.delete(file_upload.id)
            llog.gray(f"🗑️ Cleaned up uploaded file: {file_upload.id}")
            
            return {
                "success": True,
                "response": response.output_text,
                "model": model_used,
                "file_id": file_upload.id,
                "response_id": response.id
            }
            
        except Exception as e:
            llog.red(f"OpenAI API Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    def send_metadata_to_channel(self, channel_id, file_name, metadata, airtable_record=None, thread_ts=None):
        """Send formatted metadata and summary to Slack channel as a thread reply using Block Kit."""
        
        # Build structured blocks for better formatting
        base_id = os.environ.get("AIRTABLE_AI_TEACHING_AND_LEARNING_BASE")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📄 PDF Analysis Complete: {file_name}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📋 METADATA EXTRACTED:*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn", 
                        "text": f"*Title:*\n{metadata['title']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Year:*\n{metadata.get('year', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Topic:*\n{metadata['topic']}"
                    },
                    {
                        "type": "mrkdwn", 
                        "text": f"*Study Type:*\n{metadata['study_type']}"
                    }
                ]
            }
        ]
        
        # Add link field if available
        if metadata.get('link') and metadata['link'] != 'N/A':
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔗 Link:* {metadata['link']}"
                }
            })
        
        # Add summary section
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn", 
                    "text": f"*📝 SUMMARY:*\n{metadata['summary']}"
                }
            },
            {
                "type": "divider"
            }
        ])
        
        # Add footer with attribution and optional Airtable button
        footer_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🤖 Analyzed by OpenAI • 🗃️ Saved to Airtable"
            }
        }
        
        # Add Airtable button if record exists
        if airtable_record and base_id:
            footer_block["accessory"] = {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View in Airtable"
                },
                "url": f"https://airtable.com/{base_id}/{airtable_record['id']}",
                "style": "primary"
            }
        
        blocks.append(footer_block)
        
        # Send the message with blocks
        if thread_ts:
            # Reply in thread
            self.slack_client.chat_postMessage(
                channel=channel_id,
                blocks=blocks,
                text=f"PDF Analysis Complete: {file_name}",  # Fallback text for notifications
                thread_ts=thread_ts
            )
            llog.green(f"📝 Metadata and summary posted as thread reply with blocks")
        else:
            # Fallback to regular message
            self.slack_client.chat_postMessage(
                channel=channel_id,
                blocks=blocks,
                text=f"PDF Analysis Complete: {file_name}"
            )
    
    def send_error_to_channel(self, channel_id, error_message, thread_ts=None):
        """Send error message to Slack channel."""
        error_text = f"❌ **PDF Processing Error**\n\n{error_message}\n\nPlease try again or contact support."
        
        if thread_ts:
            # Reply in thread
            self.slack_client.chat_postMessage(
                channel=channel_id,
                text=error_text,
                thread_ts=thread_ts
            )
            llog.red(f"📝 Error posted as thread reply")
        else:
            # Fallback to regular message
            self.send_to_channel(channel_id, error_text)