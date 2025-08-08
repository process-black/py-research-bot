"""PDF processing utilities for downloading and text extraction."""

import os
import tempfile
import requests
from typing import Optional, Tuple
from src.utils import colored_logs as llog


def download_pdf_from_slack(file_url: str, bot_token: str) -> Optional[str]:
    """
    Download PDF from Slack to temporary file.
    
    Args:
        file_url (str): Slack file URL
        bot_token (str): Slack bot token for authentication
        
    Returns:
        str: Path to downloaded temporary file, or None if failed
    """
    try:
        llog.cyan(f"📥 Downloading PDF from Slack: {file_url}")
        
        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf', dir='/tmp')
        
        # Download file with Slack authentication
        headers = {'Authorization': f'Bearer {bot_token}'}
        response = requests.get(file_url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Write to temp file
        with os.fdopen(temp_fd, 'wb') as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
        
        file_size = os.path.getsize(temp_path)
        llog.green(f"✅ PDF downloaded successfully: {temp_path} ({file_size} bytes)")
        
        return temp_path
        
    except Exception as e:
        llog.red(f"❌ Failed to download PDF: {str(e)}")
        # Clean up temp file if it was created
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass
        return None


def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text from PDF file.
    
    Note: For now, this is a placeholder. In production, you'd use:
    - PyPDF2, pdfplumber, or pypdf for text extraction
    - Or send the PDF file directly to OpenAI's file API
    
    Args:
        pdf_path (str): Path to PDF file
        
    Returns:
        str: Extracted text, or None if failed
    """
    try:
        llog.yellow(f"📄 Extracting text from PDF: {pdf_path}")
        
        # TODO: Implement actual PDF text extraction
        # For now, return placeholder text for testing
        placeholder_text = f"""
        [PDF TEXT EXTRACTION PLACEHOLDER]
        
        This is where the actual PDF text would be extracted from: {pdf_path}
        
        In production, this would use libraries like:
        - PyPDF2: for basic text extraction
        - pdfplumber: for more sophisticated extraction
        - Or send the PDF directly to OpenAI's file API
        
        File size: {os.path.getsize(pdf_path)} bytes
        """
        
        llog.green("✅ Text extraction completed (placeholder)")
        return placeholder_text
        
    except Exception as e:
        llog.red(f"❌ Failed to extract text from PDF: {str(e)}")
        return None


def cleanup_temp_file(file_path: str) -> bool:
    """
    Clean up temporary file.
    
    Args:
        file_path (str): Path to temporary file
        
    Returns:
        bool: True if successfully deleted
    """
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            llog.gray(f"🗑️  Cleaned up temp file: {file_path}")
            return True
        return False
    except Exception as e:
        llog.red(f"❌ Failed to cleanup temp file {file_path}: {str(e)}")
        return False