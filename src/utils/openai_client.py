"""OpenAI client utility for PDF summarization and analysis."""

import os
from dotenv import load_dotenv
from openai import OpenAI
from src.utils import colored_logs as llog
from src.utils.pdf_metadata_models import PDFMetadata

# Ensure environment variables are loaded
load_dotenv()


class OpenAIClient:
    """OpenAI client wrapper for document analysis."""
    
    def __init__(self):
        """Initialize OpenAI client with API key from environment."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        llog.gray(f"🔑 Initializing OpenAI client with API key: {api_key[:10]}...")
        self.client = OpenAI(api_key=api_key)
    
    def extract_pdf_metadata(self, pdf_file_path: str, filename: str = None) -> dict:
        """
        Extract structured metadata from PDF using OpenAI with structured outputs.
        
        Args:
            pdf_file_path (str): Path to PDF file
            filename (str): Original filename for context
            
        Returns:
            dict: Structured metadata extraction result
        """
        try:
            llog.yellow("🤖 Extracting PDF metadata using structured outputs...")
            
            # Upload PDF file to OpenAI
            with open(pdf_file_path, 'rb') as pdf_file:
                file_upload = self.client.files.create(
                    file=pdf_file,
                    purpose='user_data'
                )
            
            llog.cyan(f"📤 PDF uploaded to OpenAI: {file_upload.id}")
            
            # Build context-aware metadata extraction prompt
            filename_context = ""
            if filename:
                filename_context = f"""
            
            **FILENAME CONTEXT**: The file is named "{filename}"
            
            Note: If this appears to be an ArXiv paper (format like YYMM.NNNNN[vN].pdf), the filename provides dating context:
            - YYMM format: 2508 = 2025 August, 2412 = 2024 December, etc.
            - This can help determine publication year if not explicitly stated in the document
            """
            
            extraction_prompt = f"""
            Please analyze this PDF document and extract the following structured metadata:{filename_context}

            1. **Title**: Extract the exact title of the document
            2. **Year**: Publication year (check document text first, then use filename context if ArXiv format)
            3. **Topic**: Categorize into one of the provided topic options based on the main research focus
            4. **Study Type**: Identify the research methodology type
            5. **Link**: Any URL, DOI, or web reference mentioned in the document (including ArXiv links)
            6. **Summary**: Provide a comprehensive 3-4 paragraph summary covering:
               - Main research question and objectives
               - Key methodology and approach
               - Primary findings and results
               - Significance and implications

            Focus on accuracy and be conservative with categorization. If uncertain about topic or study type, choose the closest match.
            Use filename context to supplement missing information, especially for ArXiv papers.
            """
            
            # Try models with structured output support
            models_to_try = ["gpt-5", "gpt-4o", "gpt-4o-mini"]
            
            for model in models_to_try:
                try:
                    llog.yellow(f"🎯 Trying structured extraction with: {model}")
                    
                    # Create client with timeout
                    timeout_client = OpenAI(
                        api_key=self.client.api_key,
                        timeout=180.0
                    )
                    
                    # Use Responses API with structured output for PDF files
                    response = timeout_client.responses.parse(
                        model=model,
                        input=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "input_file",
                                        "file_id": file_upload.id
                                    },
                                    {
                                        "type": "input_text",
                                        "text": extraction_prompt
                                    }
                                ]
                            }
                        ],
                        text_format=PDFMetadata
                    )
                    
                    # Get structured data directly from Responses API
                    metadata = response.output_parsed
                    
                    llog.green(f"✅ Successfully extracted metadata with {model}")
                    
                    # Cleanup uploaded file
                    self.client.files.delete(file_upload.id)
                    llog.gray(f"🗑️ Cleaned up uploaded file: {file_upload.id}")
                    
                    return {
                        "success": True,
                        "metadata": metadata.model_dump(),
                        "model": model
                    }
                    
                except Exception as e:
                    llog.yellow(f"❌ {model} failed for structured extraction: {str(e)}")
                    if model == models_to_try[-1]:  # Last model
                        raise e
                    continue
            
        except Exception as e:
            llog.red(f"OpenAI structured extraction error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "metadata": None
            }
    
    def _encode_pdf_to_base64(self, pdf_file_path: str) -> str:
        """Encode PDF file to base64 for direct upload."""
        import base64
        
        with open(pdf_file_path, 'rb') as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')
        
    
    def _estimate_cost(self, total_tokens):
        """Estimate cost based on gpt-4o-mini pricing."""
        # gpt-4o-mini pricing (approximate): $0.15 per 1M input tokens, $0.60 per 1M output tokens
        # For simplicity, using average of $0.375 per 1M tokens
        cost_per_million = 0.375
        estimated_cost = (total_tokens / 1_000_000) * cost_per_million
        return round(estimated_cost, 4)