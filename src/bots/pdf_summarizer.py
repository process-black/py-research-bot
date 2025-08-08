"""PDF Summarizer Bot - processes PDF files and creates summaries."""

import os
from src.bots.base_bot import BaseBot
from src.utils.openai_client import OpenAIClient
from src.utils.pdf_helpers import download_pdf_from_slack, extract_text_from_pdf, cleanup_temp_file
from src.utils import colored_logs as llog


class PDFSummarizerBot(BaseBot):
    """Bot that summarizes PDF files using OpenAI and stores results."""
    
    def __init__(self, slack_client=None):
        """Initialize with OpenAI client."""
        super().__init__(slack_client)
        self.openai_client = OpenAIClient()
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
            
            # Step 2: Send PDF to OpenAI for summarization
            llog.yellow("🤖 Processing with OpenAI...")
            analysis_result = self.analyze_pdf_with_openai(temp_file_path)
            
            # Step 3: Log the OpenAI response for debugging
            llog.green("🎉 OpenAI Response:")
            llog.blue(analysis_result)
            llog.divider()
            
            if analysis_result["success"]:
                # Step 4: Send results to Slack
                self.send_summary_to_channel(channel_id, file_name, analysis_result, thread_ts=thread_ts)
                llog.green(f"✅ PDF processing completed successfully: {file_name}")
            else:
                self.send_error_to_channel(channel_id, f"OpenAI analysis failed: {analysis_result.get('error', 'Unknown error')}", thread_ts=thread_ts)
                
        except Exception as e:
            llog.red(f"❌ PDF processing failed: {str(e)}")
            self.send_error_to_channel(channel_id, f"Processing failed: {str(e)}", thread_ts=thread_ts)
        
        finally:
            # Step 6: Always cleanup temp file
            if temp_file_path:
                cleanup_temp_file(temp_file_path)
    
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
            
            # Use the Responses API with file input
            response = self.openai_client.client.responses.create(
                model="gpt-4o-mini",
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
            
            # Cleanup uploaded file
            self.openai_client.client.files.delete(file_upload.id)
            llog.gray(f"🗑️ Cleaned up uploaded file: {file_upload.id}")
            
            return {
                "success": True,
                "response": response.output_text,
                "model": "gpt-4o-mini",
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
    
    def send_summary_to_channel(self, channel_id, file_name, analysis_result, thread_ts=None):
        """Send formatted summary to Slack channel as a thread reply."""
        summary_text = analysis_result["response"]
        model_used = analysis_result.get("model", "Unknown")
        
        message = f"""📄 **PDF Summary Complete: {file_name}**

{summary_text}

---
*Analysis by OpenAI {model_used}*"""
        
        if thread_ts:
            # Reply in thread
            self.slack_client.chat_postMessage(
                channel=channel_id,
                text=message,
                thread_ts=thread_ts
            )
            llog.green(f"📝 Summary posted as thread reply")
        else:
            # Fallback to regular message
            self.send_to_channel(channel_id, message)
    
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